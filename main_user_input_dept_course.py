from icalendar import Calendar, Event
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

def read_ics_file(filename, target_grade, target_department, target_course=None):
    with open(filename, 'r') as f:
        calendar = Calendar.from_ical(f.read())
        events = []
        for component in calendar.walk():
            if isinstance(component, Event):
                summary = component.get('summary', '')
                # Check if grade and department are in the summary
                if target_grade in summary and target_department in summary:
                    # If a course is specified, check if it's in the summary as well
                    if target_course is None or target_course in summary:
                        event = {
                            'summary': summary,
                            'start': component.get('dtstart').dt,
                            'end': component.get('dtend').dt,
                            'location': component.get('location'),
                            'description': component.get('description')
                        }
                        events.append(event)
        return events

def add_event_to_calendar(event, calendar_id='primary'):
    """Adds an event to Google Calendar."""
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)

    event_body = {
        'summary': event['summary'],
        'location': event.get('location', ''),
        'description': event.get('description', ''),
        'start': {
            'dateTime': event['start'].isoformat(),
            'timeZone': 'Asia/Tokyo',  # Adjust to your timezone
        },
        'end': {
            'dateTime': event['end'].isoformat(),
            'timeZone': 'Asia/Tokyo',  # Adjust to your timezone
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    try:
        event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
        print(f"Event created: {event.get('htmlLink')}")
        return event
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def main():
    # 1. Get user input for target grade
    while True:
        target_grade = input("Enter the target grade (1-4): ")
        if target_grade in ["1", "2", "3", "4"]:
            target_grade = target_grade + "年生"  # Convert to "X年生" format
            break
        else:
            print("Invalid grade. Please enter a number between 1 and 4.")

    # 2. Get user input for target department with choices
    while True:
        print("Select the target department:")
        print("1. 海事")
        print("2. 海洋")
        print("3. 流通")
        dept_choice = input("Enter the number corresponding to your department (1-3): ")

        if dept_choice == "1":
            target_department = "海事"
            break
        elif dept_choice == "2":
            target_department = "海洋"
            break
        elif dept_choice == "3":
            target_department = "流通"
            break
        else:
            print("Invalid department choice. Please enter a number between 1 and 3.")

    # 3. If the user is in 3rd or 4th year and in the "海洋" department, ask for the course
    target_course = None  # Initialize target_course
    if target_grade in ["3年生", "4年生"] and target_department == "海洋":
        while True:
            print("Select your course:")
            print("1. 制御 (Control)")
            print("2. 機関 (Engine)")
            course_choice = input("Enter the number corresponding to your course (1-2): ")

            if course_choice == "1":
                target_course = "制御"
                break
            elif course_choice == "2":
                target_course = "機関"
                break
            else:
                print("Invalid course choice. Please enter a number between 1 and 2.")

    # 4. Read events from the ICS file, filtering by target grade, department, and course
    events = read_ics_file('your_calendar_file.ics', target_grade, target_department, target_course)

    # 5. Loop through events and add them to Google Calendar
    for event in events:
        add_event_to_calendar(event)

if __name__ == '__main__':
    main()