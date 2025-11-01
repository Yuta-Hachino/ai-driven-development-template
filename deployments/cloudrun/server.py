"""
Flask server for P2P Dashboard (Cloud Run / VPS deployment)

Provides real-time dashboard with GitHub API integration.
"""

from flask import Flask, jsonify, render_template, send_from_directory
import os
import sys
from datetime import datetime, timedelta
from github import Github

# Add src to path
sys.path.insert(0, 'src')

app = Flask(
    __name__,
    static_folder='dashboard',
    template_folder='dashboard'
)

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'user/repo')
PORT = int(os.environ.get('PORT', 8080))


@app.route('/')
def index():
    """Serve the dashboard"""
    return send_from_directory('dashboard', 'index.html')


@app.route('/api/status')
def status():
    """Get current system status"""
    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(GITHUB_REPO)

        # Get recent workflow runs
        workflows = repo.get_workflow_runs()
        p2p_runs = [
            run for run in workflows[:10]
            if 'p2p' in run.name.lower()
        ]

        active_runs = [
            run for run in p2p_runs
            if run.status == 'in_progress'
        ]

        return jsonify({
            'active_instances': len(active_runs),
            'total_runs': len(p2p_runs),
            'recent_runs': [
                {
                    'id': run.id,
                    'name': run.name,
                    'status': run.status,
                    'conclusion': run.conclusion,
                    'created_at': run.created_at.isoformat(),
                    'updated_at': run.updated_at.isoformat()
                }
                for run in p2p_runs[:5]
            ]
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'active_instances': 0,
            'total_runs': 0
        }), 500


@app.route('/api/metrics')
def metrics():
    """Prometheus-compatible metrics endpoint"""
    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(GITHUB_REPO)

        # Get workflow statistics
        workflows = list(repo.get_workflow_runs()[:50])
        p2p_workflows = [w for w in workflows if 'p2p' in w.name.lower()]

        active = len([w for w in p2p_workflows if w.status == 'in_progress'])
        completed = len([w for w in p2p_workflows if w.conclusion == 'success'])
        failed = len([w for w in p2p_workflows if w.conclusion == 'failure'])

        # Prometheus format
        output = f"""# HELP autonomous_dev_active_instances Number of active P2P instances
# TYPE autonomous_dev_active_instances gauge
autonomous_dev_active_instances {active}

# HELP autonomous_dev_runs_completed_total Total completed workflow runs
# TYPE autonomous_dev_runs_completed_total counter
autonomous_dev_runs_completed_total {completed}

# HELP autonomous_dev_runs_failed_total Total failed workflow runs
# TYPE autonomous_dev_runs_failed_total counter
autonomous_dev_runs_failed_total {failed}

# HELP autonomous_dev_runs_total Total workflow runs
# TYPE autonomous_dev_runs_total counter
autonomous_dev_runs_total {len(p2p_workflows)}
"""

        return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return f"# Error: {str(e)}\n", 500, {'Content-Type': 'text/plain'}


@app.route('/api/issues/<int:issue_number>')
def get_issue_coordination(issue_number):
    """Get P2P coordination data from a specific issue"""
    try:
        gh = Github(GITHUB_TOKEN)
        repo = gh.get_repo(GITHUB_REPO)
        issue = repo.get_issue(issue_number)

        comments = list(issue.get_comments())

        # Parse coordination messages
        nodes = []
        tasks = []
        progress_reports = []

        for comment in comments:
            body = comment.body

            if body.startswith('📡 NODE_ANNOUNCE|'):
                try:
                    import json
                    data = json.loads(body.split('|', 1)[1])
                    nodes.append(data)
                except:
                    pass

            elif body.startswith('📦 TASKS_DATA|'):
                try:
                    import json
                    data = json.loads(body.split('|', 1)[1])
                    tasks = list(data.values())
                except:
                    pass

            elif body.startswith('📊 PROGRESS|'):
                try:
                    import json
                    data = json.loads(body.split('|', 1)[1])
                    progress_reports.append(data)
                except:
                    pass

        return jsonify({
            'issue_number': issue_number,
            'issue_title': issue.title,
            'nodes': nodes,
            'tasks': tasks,
            'progress_reports': progress_reports,
            'total_comments': len(comments)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=PORT, debug=True)
