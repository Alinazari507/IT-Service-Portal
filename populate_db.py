import sys
import os
from app import app, db
from models import Service

# Sample data representing the original IT portal services
sample_services = [
    {
        'name': 'Lenovo ThinkPad X1',
        'availability': 'Sofort verfügbar',
        'description_business': 'Premium Business Notebook für mobiles Arbeiten.',
        'sla': '3 Werktage',
        'costs': '0€ (Standard)'
    },
    {
        'name': 'Microsoft 365 Business',
        'availability': '24h Aktivierung',
        'description_business': 'Vollständiges Office-Paket für produktives Arbeiten.',
        'sla': '1 Werktag',
        'costs': '12,50€ / Monat'
    },
    {
        'name': 'VPN-Fernzugriff',
        'availability': 'Sofort',
        'description_business': 'Sicherer Zugriff auf das Firmennetzwerk von Zuhause.',
        'sla': '1 Stunde',
        'costs': '0€'
    },
    {
        'name': 'IT-Support Ticket',
        'availability': 'Mo-Fr 08:00-17:00',
        'description_business': 'Unterstützung bei technischen Problemen aller Art.',
        'sla': '4 Stunden',
        'costs': '0€'
    }
]

def populate():
    with app.app_context():
        try:
            # Optional: Clear existing data to avoid duplicates
            db.session.query(Service).delete()
            
            for data in sample_services:
                new_service = Service(
                    name=data['name'],
                    availability=data['availability'],
                    description_business=data['description_business'],
                    sla=data['sla'],
                    costs=data['costs']
                )
                db.session.add(new_service)
            
            db.session.commit()
            print("Database populated successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    populate()