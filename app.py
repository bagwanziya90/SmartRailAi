from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))
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

    source = request.args.get("source", "")
    destination = request.args.get("destination", "")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if source and destination:

        query = """
        SELECT * FROM trains
        WHERE LOWER(source) = LOWER(%s)
        AND LOWER(destination) = LOWER(%s)
        """

        cursor.execute(query, (source, destination))

    else:

        cursor.execute("SELECT * FROM trains")

    train_list = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "trains.html",
        trains=train_list,
        source=source,
        destination=destination
    )


# ---------------- BOOKING PAGE ----------------
@app.route("/bookings", 
methods=["GET", "POST"])
def bookings():

    message = ""

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        phone = request.form.get("phone")
        journey_date = request.form.get("journey_date")
        seats = int(request.form.get("seats"))
        train_id = request.form.get("train_id")


        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Find train
        cursor.execute(
            "SELECT * FROM trains WHERE train_id = %s",
            (train_id,)
        )

        train = cursor.fetchone()

        if train is None:
            message = "Train not found."

        elif train.get("seats", 0) < seats:
            message = "Not enough seats available."

        else:

            total_fare = train["fare"] * seats

            # Insert passenger
            cursor.execute(
                """
                INSERT INTO passengers
                (name, age, gender, phone)
                VALUES (%s, %s, %s, %s)
                """,
                (name, age, gender, phone)
            )

            passenger_id = cursor.lastrowid

            # Insert booking
            cursor.execute(
                """
                INSERT INTO bookings
                (passenger_id, train_id, journey_date,
                 seats_booked, total_fare)
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

            # Reduce seats
            cursor.execute(
                """
                UPDATE trains
                SET seats = seats - %s
                WHERE train_id = %s
                """,
                (seats, train_id)
            )

            db.commit()

            message = (
                "Ticket booked successfully! "
                f"Total Fare: ₹{total_fare}"
            )

        cursor.close()
        db.close()

    # Get all trains for booking dropdown
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM trains")
    train_list = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "bookings.html",
        trains=train_list,
        message=message
    )



# ---------------- AI SMART SEARCH ----------------

@app.route("/ai-search")
def ai_search():

    query = request.args.get("query", "").lower()

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Simple AI-style keyword understanding
    if "mumbai" in query and "pune" in query:

        cursor.execute("""
        SELECT * FROM trains
        WHERE LOWER(source) = 'mumbai'
        AND LOWER(destination) = 'pune'
        """)

    elif "pune" in query and "mumbai" in query:

        cursor.execute("""
        SELECT * FROM trains
        WHERE LOWER(source) = 'pune'
        AND LOWER(destination) = 'mumbai'
        """)

    elif "delhi" in query:

        cursor.execute("""
        SELECT * FROM trains
        WHERE LOWER(destination) = 'delhi'
        """)

    else:

        cursor.execute("SELECT * FROM trains")

    results = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "trains.html",
        trains=results,
        source="AI Search",
        destination=query
    )


# ---------------- RUN APPLICATION ----------------

if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000,debug=True)
