import datetime
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Generator

import connexion  # type: ignore
import flask
import pydantic
from flask import g
from pydantic import create_model
from sqlalchemy.orm import Session

# Helpers
from backend_engineer_interview import models, db


class PydanticBaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Get a plain SQLAlchemy Session."""
    session = g.get("db")
    if session is None:
        raise Exception("No database session available in application context")

    yield session


def get_request():
    return connexion.request


@dataclass
class StartEndDates:
    start_date: date
    end_date: date


# Implement

def split_start_end_dates(start_date: date, end_date: date, split_date: date):
    dates_before = None
    dates_after = None

    if start_date < split_date:
        dates_before = StartEndDates(
            start_date=start_date, end_date=end_date)
    if end_date > split_date:
        dates_after = StartEndDates(
            start_date=start_date, end_date=end_date)
    if start_date == split_date:
        dates_before = StartEndDates(
            start_date=split_date, end_date=start_date)
        if end_date > split_date:
            dates_after.start_date = split_date + timedelta(days=1)

    return dates_before, dates_after


def status():
    with db_session() as session:
        session.execute("SELECT 1;").one()
        return flask.make_response(flask.jsonify({"status": "up"}), 200)


class EmployeeResponse(PydanticBaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: date


class EmployeeRequest(PydanticBaseModel):
    first_name: str
    last_name: str


class ApplicationResponse(PydanticBaseModel):
    id: int
    leave_start_date: date
    leave_end_date: date
    employee: create_model('employee', first_name=(str, ...))


class ApplicationRequest(PydanticBaseModel):
    leave_start_date: str
    leave_end_date: str
    employee_id: int


def get_employee(id):
    # get db session
    with db.DBContext() as session:
        session: Session
        # get employee by id and if not found return status_code 404
        employee: models.Employee = session.query(models.Employee).filter(
            models.Employee.id == id).first()
        if not employee:
            return {'message': 'No such employee'}, 404
        # Return EmployeeResponse class from Model
        return EmployeeResponse.from_orm(employee).dict(), 200


def patch_employee(id):
    employee_request_json = get_request().get_json()
    # Validate request body
    if not employee_request_json.get('last_name'):
        return {'message': 'last_name cannot be blank'}, 400
    if not employee_request_json.get('first_name'):
        return {'message': 'first_name cannot be blank'}, 400

    # get db session
    with db.DBContext() as session:
        session: Session
        # initialize EmployeeRequest class with request body
        employee_request = EmployeeRequest(**employee_request_json)
        # update employee by id and if not found return status_code 404
        employee_is_updated = session.query(models.Employee).filter(
            models.Employee.id == id).update(
            {
                'first_name': employee_request.first_name,
                'last_name': employee_request.last_name
            })
        session.commit()
        # If employee_is_updated is False; the employee wasn't found
        if not employee_is_updated:
            return {'message': 'No such employee'}, 404

        return "Successfully updated employee", 204


def post_application():
    """
    Accepts a leave_start_date, leave_end_date, employee_id and creates an
    Application
    with those properties.  It should then return the new application with a
    status code of 200.

    If any of the properties are missing in the request body, it should
    return the new application
    with a status code of 400.

    Verify the handler using the test cases in TestPostApplication.  Add any
    more tests you think
    are necessary.
    """
    application_request_json = get_request().get_json()
    # Validate request body
    if not application_request_json.get('leave_start_date') or not \
            application_request_json.get('leave_end_date'):
        return {
                   'message': 'leave_start_date is missing;'
                              'leave_end_date is missing'
               }, 400
    if not application_request_json.get('employee_id'):
        return {'message': 'employee_id cannot be blank'}, 400
    # Check that leave_end_date and leave_start_date are valid date string
    leave_end_date = application_request_json.get('leave_end_date')
    leave_start_date = application_request_json.get('leave_start_date')
    try:
        end_date_obj = datetime.datetime.strptime(leave_end_date, '%Y-%m-%d')
        start_date_obj = datetime.datetime.strptime(
            leave_start_date, '%Y-%m-%d')
    except ValueError:
        return {'message': 'leave_start_date is invalid;'
                           'leave_end_date is invalid'
                }, 400
    # Check that leave_start_date isn't in the past and leave_end_date is not
    # before leave_start_date
    # if start_date_obj.date() < datetime.datetime.now().date():
    #     return {'message': 'leave_start_date cannot be in the past'}, 400
    if end_date_obj.date() < start_date_obj.date():
        return {'message': 'leave_end_date cannot be before '
                           'leave_start_date'}, 400

    # get db session
    with db.DBContext() as session:
        session: Session
        # initialize ApplicationRequest class with request body
        application_request = ApplicationRequest(**application_request_json)
        employer_id = application_request.employee_id
        # Check if employee exist
        employee: models.Employee = session.query(models.Employee).filter(
            models.Employee.id == employer_id).first()
        if not employee:
            return {'message': 'No such employee'}, 404

        application = models.Application(
            leave_end_date=end_date_obj,
            leave_start_date=start_date_obj,
            employee_id=application_request.employee_id
        )
        session.add(application)
        session.commit()
        session.refresh(application)
        response = {
            'id': application.id,
            'leave_start_date': application.leave_start_date,
            'leave_end_date': application.leave_end_date,
            'employee': {'first_name': application.employee.first_name}
        }
        # Return ApplicationResponse class from json
        return ApplicationResponse(**response).dict(), 200
