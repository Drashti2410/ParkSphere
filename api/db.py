from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///data/parking.db")
Base = declarative_base()

class ParkingEvent(Base):
    __tablename__ = "parking_events"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    distance_cm = Column(Float)
    slot_status = Column(String)
    gate_status = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_event(distance_cm, slot_status, gate_status):
    session = Session()
    event = ParkingEvent(distance_cm=distance_cm, slot_status=slot_status, gate_status=gate_status)
    session.add(event)
    session.commit()
    session.close()

def get_recent_events(limit=50):
    session = Session()
    events = session.query(ParkingEvent).order_by(ParkingEvent.timestamp.desc()).limit(limit).all()
    session.close()
    return [{"timestamp": e.timestamp.isoformat(), "distance_cm": e.distance_cm,
             "slot_status": e.slot_status, "gate_status": e.gate_status} for e in events]

def get_occupancy_stats():
    session = Session()
    total = session.query(ParkingEvent).count()
    occupied = session.query(ParkingEvent).filter_by(slot_status="Occupied").count()
    session.close()
    return {"total_events": total, "occupied_pct": round(occupied / total * 100, 1) if total else 0}
