"""
Główny moduł sterujący aplikacji webowej Service Desk.
"""

import os
import io
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from openpyxl import Workbook

# Importy lokalne
from utils import safe_json_load, add_log
from models import db, User, Ticket, Notification

app = Flask(__name__)
app.secret_key = "40061aa3ee5b2533080503e5c91cedf1d70a2cdafacd77a2"

# --- Konfiguracja bazy danych i środowiska ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://it_user:inzynier2026!@192.168.30.10/service_desk_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicjalizacja bazy danych i migracji
db.init_app(app)
migrate = Migrate(app, db)

# Konfiguracja systemu plików dla załączników
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# --- Warstwa kontrolera (obsługa tras) ---

@app.route("/", methods=["GET", "POST"])
def login():
    """Obsługuje proces uwierzytelniania użytkowników w systemie"""
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Błędny login lub hasło")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Zamyka sesję i przekierowuje do logowania"""
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    """Wyświetla główny panel sterowania zgłoszeniami"""
    if "user_id" not in session: return redirect(url_for("login"))
    
    user_id = session["user_id"]
    role = session["role"]
    query = request.args.get("q", "").strip()
    
    notifs = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    
    if role == "consultant":
        t_query = Ticket.query.filter_by(creator_id=user_id)
    else:
        t_query = Ticket.query

    if query:
        t_query = t_query.filter(Ticket.title.ilike(f"%{query}%") | Ticket.case_number.ilike(f"%{query}%"))

    tickets = t_query.order_by(Ticket.created_at_dt.desc()).all()
    return render_template("dashboard.html", role=role, tickets=tickets, notifications=notifs, query=query)

@app.route("/create_ticket", methods=["GET", "POST"])
def create_ticket():
    """Inicjuje nowe zgłoszenie serwisowe"""
    if "user_id" not in session or session["role"] != "consultant":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        today = datetime.now().strftime("%Y-%m-%d")
        count = Ticket.query.filter(Ticket.created_at == today).count() + 1
        case_no = f"IT-{today}-{count:03d}"

        ticket = Ticket(
            case_number=case_no,
            title=request.form.get("title"),
            description=request.form.get("description"),
            service=request.form.get("service"),
            account_status=request.form.get("account_status"),
            cache_status=request.form.get("cache_status"),
            email=request.form.get("email"),
            client_number=request.form.get("client_number"),
            client_name=request.form.get("client_name"),
            pesel_nip=request.form.get("pesel_nip"),
            invoice_number=request.form.get("invoice_number"),
            version=request.form.get("version"),
            model=request.form.get("model"),
            os_info=request.form.get("os"),
            creator_id=session["user_id"],
            created_at=today,
            status="Nowe",
            logs=json.dumps([]),
            notes=json.dumps([]),
            attachments=json.dumps([])
        )
        
        files = request.files.getlist("attachments")
        attached = []
        for f in files:
            if f and f.filename:
                fname = secure_filename(f.filename)
                f.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
                attached.append(fname)
        
        ticket.attachments = json.dumps(attached)
        add_log(ticket, "Utworzono zgłoszenie")
        
        db.session.add(ticket)
        db.session.flush()

        db.session.add(Notification(
            user_id=session["user_id"], 
            ticket_id=ticket.id, 
            message=f"Pomyślnie utworzono zgłoszenie {ticket.case_number}"
        ))
        
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("create_ticket.html")

@app.route("/view_ticket/<int:ticket_id>", methods=["GET", "POST"])
def view_ticket(ticket_id):
    """Szczegóły zgłoszenia i komunikacja IT/Konsultant"""
    if "user_id" not in session: return redirect(url_for("login"))
    
    t = Ticket.query.get_or_404(ticket_id)
    role = session["role"]
    
    if role == "it" and t.status == "Nowe":
        t.status = "W trakcie realizacji"
        add_log(t, "IT otworzył zgłoszenie")
        db.session.add(Notification(user_id=t.creator_id, ticket_id=t.id, message=f"IT sprawdza Twoje zgłoszenie: {t.case_number}"))
        db.session.commit()

    if request.method == "POST":
        note_text = request.form.get("note")
        sol_text = request.form.get("solution")
        
        if note_text:
            notes = safe_json_load(t.notes)
            notes.append(f"{datetime.now().strftime('%H:%M')} {role.upper()}: {note_text}")
            t.notes = json.dumps(notes)
            add_log(t, f"Dodano komentarz ({role})")

        if role == "it" and sol_text:
            t.solution = sol_text
            t.status = "Zamknięte"
            t.closed_at_dt = datetime.now()
            add_log(t, "IT zamknął zgłoszenie")
            db.session.add(Notification(user_id=t.creator_id, ticket_id=t.id, message=f"Zgłoszenie {t.case_number} zostało rozwiązane!"))

        db.session.commit()
        return redirect(url_for("view_ticket", ticket_id=t.id))

    t.notes_list = safe_json_load(t.notes)
    t.logs_list = safe_json_load(t.logs)
    t.attachments_list = safe_json_load(t.attachments)
    return render_template("view_ticket.html", ticket=t, role=role)

@app.route("/download_report", methods=["POST"])
def download_report():
    """Generuje raport SLA w formacie XLSX"""
    if session.get("role") != "it":
        return redirect(url_for("login"))
        
    tickets = Ticket.query.all()
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "Numer", "Tytuł", "Status", "Czas realizacji (h)"])
    
    for t in tickets:
        sla = ""
        if t.closed_at_dt and t.created_at_dt:
            diff = t.closed_at_dt - t.created_at_dt
            sla = round(diff.total_seconds() / 3600, 2)
        ws.append([t.id, t.case_number, t.title, t.status, sla])
    
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    
    return send_file(
        out, 
        as_attachment=True, 
        download_name=f"raport_zgloszen_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/clear_notifications", methods=["POST"])
def clear_notifications():
    if "user_id" in session:
        Notification.query.filter_by(user_id=session["user_id"]).update({"is_read": True})
        db.session.commit()
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 403

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Seeding użytkowników
        users_config = [
            {"u": "it", "p": "it", "r": "it"},
            {"u": "konsultant1", "p": "haslo", "r": "consultant"}
        ]
        for data in users_config:
            if not User.query.filter_by(username=data["u"]).first():
                new_user = User(
                    username=data["u"],
                    password_hash=generate_password_hash(data["p"]),
                    role=data["r"]
                )
                db.session.add(new_user)
        db.session.commit()

    app.run(host='192.168.20.10', port=443, ssl_context='adhoc', debug=False)