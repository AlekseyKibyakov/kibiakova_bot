import sqlalchemy as sq
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

def create_tables(engine):
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'user'
    
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    tg_id = sq.Column(sq.VARCHAR(100), unique=True)
    first_name = sq.Column(sq.VARCHAR(100))
    last_name = sq.Column(sq.VARCHAR(100))
    email = sq.Column(sq.VARCHAR(200), unique=True)
    phone = sq.Column(sq.VARCHAR(100), unique=True)
    
    def __str__(self):
        return [self.id, self.tg_id,
                self.first_name, self.last_name,
                self.email, self.phone, self.events]

    
class Event(Base):
    __tablename__ = 'event'
    
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    title = sq.Column(sq.VARCHAR(150))
    date = sq.Column(sq.DateTime)
    users = relationship('User', secondary='user_event', backref='events', cascade='delete')
    
    def __str__(self):
        return [self.id, self.title,
                self.date, self.users]


user_event = sq.Table(
    'user_event',
    Base.metadata,
    sq.Column('user_id', sq.ForeignKey('user.id', ondelete='CASCADE')),
    sq.Column('event_id', sq.ForeignKey('event.id', ondelete='CASCADE')),
)