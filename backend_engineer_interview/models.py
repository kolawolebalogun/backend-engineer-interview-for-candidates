from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=Base)  # type: ignore


class Employee(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(Date)
    secret = Column(String)

    application = relationship("Application", back_populates="employee")


class Application(Base):
    id = Column(Integer, primary_key=True)
    leave_start_date = Column(Date)
    leave_end_date = Column(Date)
    employee_id = Column(String, ForeignKey("employee.id"), nullable=False)

    employee = relationship("Employee", back_populates="application")
