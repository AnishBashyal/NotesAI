import firebase_admin 
import json
from flask import Flask, render_template, request, jsonify, session, url_for, redirect, Blueprint
from firebase_admin import db, credentials


main = Blueprint('main', __name__)

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://notesai-403418-default-rtdb.firebaseio.com/"})


@main.route("/add_note", methods=['POST'])
def add_note():
    print("add note")
    if request.method == 'POST':
        data = request.get_json()
        note = data.get('note')
        user_id = data.get('user_id')
        notes_ref = db.reference('/notes')
        print(user_id, note)
        new_note_data = {
            'user_id': user_id,
            'note': note
        }

        new_note_ref = notes_ref.push(new_note_data)

        return new_note_ref.key

@main.route("/note/<string:note_id>", methods=['GET'])
def get_note(note_id):
    notes_ref = db.reference('/notes')

    all_notes = notes_ref.get()

    if all_notes:
        selected_note = all_notes.get(note_id)
        return selected_note.get('note')

@main.route("/delete_note", methods=['POST'])
def remove_note():
    if request.method == 'POST':
        data = request.get_json()
        note_id = data.get('note_id')
        ref = db.reference('/notes/'+note_id)
        ref.delete()
        return redirect(url_for('get_notes'))
    
@main.route("/user_notes/<string:user_id>", methods=['GET'])
def user_notes(user_id):
    
    notes_ref = db.reference('/notes')

    all_notes = notes_ref.get()

    if all_notes:
        user_notes = [[note_data, note_id] for note_id, note_data in all_notes.items() if note_data.get('user_id') == user_id]
        if user_notes:
            return user_notes
        else:
            print(f"No notes found for user_id: {user_id}")
    else:
        print("No notes found in the database.") 
    return None


