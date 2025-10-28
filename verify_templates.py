#!/usr/bin/env python3
"""
Quick script to verify program templates are accessible
"""
import sqlite3

def verify_templates():
    print("=" * 60)
    print("PROGRAM TEMPLATES VERIFICATION")
    print("=" * 60)

    db = sqlite3.connect('trainer_dashboard.db')
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    # Check templates
    templates = cursor.execute('SELECT * FROM program_templates ORDER BY id').fetchall()

    print(f"\n✓ Found {len(templates)} program templates in database:\n")

    for template in templates:
        exercises = cursor.execute(
            'SELECT COUNT(*) as count FROM program_template_exercises WHERE template_id = ?',
            (template['id'],)
        ).fetchone()

        print(f"  {template['id']}. {template['name']}")
        print(f"     └─ {exercises['count']} exercises")
        print(f"     └─ {template['description'][:60]}...")
        print()

    db.close()

    print("=" * 60)
    print("HOW TO ACCESS IN WEB APP:")
    print("=" * 60)
    print("\n1. Start the app:")
    print("   python3 app.py")
    print("\n2. Login as trainer:")
    print("   Username: trainer1")
    print("   Password: password123")
    print("\n3. Look for 'Templates' link in top navigation")
    print("   (Between 'Exercises' and 'Analytics')")
    print("\n4. Or navigate directly to:")
    print("   http://localhost:5000/trainer/program-templates")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    verify_templates()
