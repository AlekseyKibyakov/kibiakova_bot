import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from config import CONNSTR, DB_LOGIN
from models import create_tables, User, Event

DSN = f'postgresql://{DB_LOGIN["login"]}:\
{DB_LOGIN["password"]}@{DB_LOGIN["host"]}:\
{DB_LOGIN["port"]}/{DB_LOGIN["database"]}'

engine = sq.create_engine(CONNSTR)
create_tables(engine)
Session = sessionmaker(bind=engine)
session = Session()


def update_user_events(user_tg_id, event_title):
    for e in get_events_from_db():
        if e.title == event_title:
            event = e
    for user in session.query(User).all():
        if user.tg_id == str(user_tg_id):
            if event not in user.events:
                user.events.append(event)
                session.commit()
                session.close()
                return True
            else:
                return True
    return False


def _check_is_in_db(item, event):
    '''Check if item is in database'''
    if isinstance(item, User):
        for user in session.query(User).all():
            if user.tg_id == item.tg_id:
                if event not in user.events:
                    user.events.append(event)
                    session.commit()
                    return True
                return True
    elif isinstance(item, Event):
        s = session.query(Event).all()
        for e in session.query(Event).all():
            if e.title == item.title:
                return True
    return False


def add_item_to_db(item, event=None):
    '''Add person to database (no matter user or candidate)'''
    if _check_is_in_db(item, event):
        session.close()
        return
    session.add(item)
    commit_session()
    close_session()


def delete_event(event_title):
    event_to_delete = session.query(Event).filter(Event.title == event_title).first()
    session.delete(event_to_delete)
    commit_session()
    close_session()
    


def get_events_from_db():
    events = []
    for e in session.query(Event).all():
        events.append(e)
    return events


def commit_session():
    '''Send all changes to database'''
    session.commit()


def close_session():
    '''The end of the session.
    Can be called once at the end
    of the running code'''
    session.close()
