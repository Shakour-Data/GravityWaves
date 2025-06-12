from datetime import datetime

def calculate_importance(activity, activities_dict):
    """
    Calculate importance score for an activity.
    Criteria:
    - Number of dependent activities (postrequisites)
    - Priority (if defined as an attribute, else default)
    - Impact (can be extended)
    """
    # Base importance score
    importance = 0

    # Count number of activities that depend on this activity (postrequisites)
    postrequisites_count = len(activity.postrequisites.all()) if hasattr(activity, 'postrequisites') else 0
    importance += postrequisites_count * 2  # weight for dependencies

    # Priority attribute (if exists)
    priority = getattr(activity, 'priority', None)
    if priority is not None:
        importance += priority * 3  # weight for priority

    # Impact can be added here if defined

    return importance

def calculate_urgency(activity):
    """
    Calculate urgency score for an activity.
    Criteria:
    - Deadline proximity (closer deadline means higher urgency)
    - Status (e.g., not started but deadline near is urgent)
    """
    urgency = 0
    now = datetime.utcnow()

    # Assume activity has a deadline attribute (datetime), else no urgency from deadline
    deadline = getattr(activity, 'deadline', None)
    if deadline:
        delta = (deadline - now).total_seconds()
        if delta < 0:
            # Past deadline, very urgent
            urgency += 10
        else:
            # Closer deadline, higher urgency (inverse proportional)
            urgency += max(0, 10 - delta / 8640)  # scale over 10 days

    # Status urgency
    status = getattr(activity, 'status', 'Not Started')
    if status == 'Not Started' and urgency > 0:
        urgency += 5  # boost urgency if not started and deadline near

    return urgency

def calculate_delay(activity):
    """
    Calculate delay in days for an activity.
    Delay = actual_end_date - planned_end_date
    """
    planned_end = getattr(activity, 'planned_end_date', None)
    actual_end = getattr(activity, 'actual_end_date', None)
    if planned_end and actual_end:
        delay = (actual_end - planned_end).days
        return max(0, delay)
    return 0

def calculate_progress(activity):
    """
    Calculate progress percentage for an activity based on tasks completion.
    """
    tasks = getattr(activity, 'tasks', None)
    if not tasks:
        return 0
    total_tasks = tasks.count()
    if total_tasks == 0:
        return 0
    completed_tasks = tasks.filter_by(status='Completed').count()
    progress = (completed_tasks / total_tasks) * 100
    return progress

def generate_report(project):
    """
    Generate a report dictionary for a project including:
    - List of activities with importance, urgency, delay, progress
    - Summary statistics
    """
    report = {}
    activities = project.activities.all()
    report['project_name'] = project.name
    report['activities'] = []

    total_activities = len(activities)
    total_progress = 0
    total_delay = 0

    for activity in activities:
        importance = calculate_importance(activity, activities)
        urgency = calculate_urgency(activity)
        delay = calculate_delay(activity)
        progress = calculate_progress(activity)

        total_progress += progress
        total_delay += delay

        report['activities'].append({
            'id': activity.id,
            'name': activity.name,
            'importance': importance,
            'urgency': urgency,
            'delay': delay,
            'progress': progress,
            'status': getattr(activity, 'status', 'Not Started')
        })

    report['summary'] = {
        'total_activities': total_activities,
        'average_progress': total_progress / total_activities if total_activities > 0 else 0,
        'total_delay': total_delay
    }

    return report
