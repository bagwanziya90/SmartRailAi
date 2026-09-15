from flask import Flask, render_template, request
import mysql.connector
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(base_dir, "templates")
)


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- TRAIN SEARCH ----------------

@app.route("/trains")
def trains():

    source = request.args.get("source", "").strip()
    destination = request.args.get("destination", "").strip()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        if source and destination:

            query = """
                SELECT *
                FROM trains
                WHERE LOWER(source) = LOWER(%s)
                AND LOWER(destination) = LOWER(%s)
            """

            cursor.execute(query, (source, destination))

        else:

            cursor.execute("SELECT * FROM trains")

        train_list = cursor.fetchall()

    finally:

        cursor.close()
        db.close()

    return render_template(
        "trains.html",
        trains=train_list,
        source=source,
        destination=destination
    )


# ---------------- BOOKING PAGE ----------------

@app.route("/booking", methods=["GET", "POST"])
def booking():

    message = ""

    # ---------------- BOOK TICKET ----------------

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()
        journey_date = request.form.get("journey_date", "").strip()
        train_id = request.form.get("train_id", "").strip()

        # Validate seats
        try:
            seats = int(request.form.get("seats", 0))
        except (ValueError, TypeError):
            seats = 0

        # Validate passenger details
        if not name or not age or not gender or not phone:

            message = "Please fill in all passenger details."

        elif not journey_date or not train_id:

            message = "Please select a train and journey date."

        elif seats <= 0:

            message = "Please select at least one seat."

        else:

            db = get_db_connection()
            cursor = db.cursor(dictionary=True)

            try:

                # Start transaction
                db.start_transaction()

                # Lock selected train
                cursor.execute(
                    """
                    SELECT *
                    FROM trains
                    WHERE train_id = %s
                    FOR UPDATE
                    """,
                    (train_id,)
                )

                train = cursor.fetchone()

                if train is None:

                    message = "Train not found."
                    db.rollback()

                elif train.get("seats", 0) < seats:

                    message = "Not enough seats available."
                    db.rollback()

                else:

                    # Calculate fare
                    total_fare = train["fare"] * seats

                    # Insert passenger
                    cursor.execute(
                        """
                        INSERT INTO passengers
                        (name, age, gender, phone)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            name,
                            age,
                            gender,
                            phone
                        )
                    )

                    passenger_id = cursor.lastrowid

                    # Insert booking
                    cursor.execute(
                        """
                        INSERT INTO bookings
                        (
                            passenger_id,
                            train_id,
                            journey_date,
                            seats_booked,
                            total_fare
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            passenger_id,
                            train_id,
                            journey_date,
                            seats,
                            total_fare
                        )
                    )

                    # Reduce available seats
                    cursor.execute(
                        """
                        UPDATE trains
                        SET seats = seats - %s
                        WHERE train_id = %s
                        """,
                        (
                            seats,
                            train_id
                        )
                    )

                    # Save changes
                    db.commit()

                    message = (
                        "Ticket booked successfully! "
                        f"Total Fare: ₹{total_fare}"
                    )

            except mysql.connector.Error as error:

                db.rollback()

                message = f"Booking failed: {error}"

            finally:

                cursor.close()
                db.close()

    # ---------------- GET ALL TRAINS ----------------

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute("SELECT * FROM trains")
        train_list = cursor.fetchall()

    finally:

        cursor.close()
        db.close()

    # IMPORTANT:
    # Use the SAME HTML filename here.
    return render_template(
        "booking.html",
        trains=train_list,
        message=message
    )


# ---------------- AI SMART SEARCH ----------------

@app.route("/ai-search")
def ai_search():

    query = request.args.get("query", "").lower().strip()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # Mumbai → Pune
        if "mumbai" in query and "pune" in query:

            cursor.execute(
                """
                SELECT *
                FROM trains
                WHERE LOWER(source) = 'mumbai'
                AND LOWER(destination) = 'pune'
                """
            )

        # Pune → Mumbai
        elif "pune" in query and "mumbai" in query:

            cursor.execute(
                """
                SELECT *
                FROM trains
                WHERE LOWER(source) = 'pune'
                AND LOWER(destination) = 'mumbai'
                """
            )

        # Any train going to Delhi
        elif "delhi" in query:

            cursor.execute(
                """
                SELECT *
                FROM trains
                WHERE LOWER(destination) = 'delhi'
                """
            )

        # No recognized route
        else:

            cursor.execute("SELECT * FROM trains")

        results = cursor.fetchall()

    finally:

        cursor.close()
        db.close()

    return render_template(
        "trains.html",
        trains=results,
        source="AI Search",
        destination=query
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
