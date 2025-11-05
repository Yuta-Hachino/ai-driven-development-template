# Extended Roadmap - Advanced Features (Phase 6-8)

This document outlines the extended development roadmap for advanced AI-driven features that build upon the core autonomous development system (Phase 1-5).

## 🎯 Vision

Transform the autonomous development system from a multi-instance collaboration platform into an **intelligent, self-optimizing, cross-repository development ecosystem** with:

1. **Machine Learning-Based Intelligence** - Predictive task allocation and performance optimization
2. **Real-time Human Collaboration** - Interactive UI for monitoring and controlling autonomous development
3. **Enterprise-Scale Coordination** - Cross-repository collaboration for microservices and distributed systems

## 📋 Overview

| Phase | Name | Duration | Est. Lines | Priority |
|-------|------|----------|------------|----------|
| Phase 6 | ML-Based Task Optimization | Week 11-13 (3 weeks) | 3,000+ | High |
| Phase 7 | Real-time Collaboration UI | Week 14-16 (3 weeks) | 4,000+ | High |
| Phase 8 | Cross-Repository Collaboration | Week 17-20 (4 weeks) | 5,000+ | Medium |

**Prerequisites**: Phases 1-5 must be completed and production-ready before starting extended features.

---

## 🤖 Phase 6: ML-Based Task Optimization

**Duration**: Week 11-13 (3 weeks)
**Goal**: Leverage machine learning to optimize task allocation, predict performance, and prevent bottlenecks

### Motivation

Current Phase 3 implementation uses rule-based task assignment (skill matching + load balancing). While effective, it cannot:
- Learn from historical patterns
- Predict task completion times
- Anticipate bottlenecks before they occur
- Optimize for multiple objectives simultaneously (speed, cost, quality)

Machine learning enables the system to continuously improve its decision-making based on real-world outcomes.

### Detailed Components

#### 1. Task Completion Time Prediction

**Problem**: Accurate time estimation is critical for planning and resource allocation.

**Solution**: Supervised learning model trained on historical task execution data.

**Implementation** (`src/ml/prediction/task_predictor.py`):

```python
from typing import Dict, List
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import joblib

class TaskCompletionPredictor:
    """Predicts task completion time using ensemble ML models"""

    def __init__(self, model_path: Optional[str] = None):
        self.models = {
            'rf': RandomForestRegressor(n_estimators=100, max_depth=10),
            'gb': GradientBoostingRegressor(n_estimators=100, max_depth=5)
        }
        self.scaler = StandardScaler()
        self.feature_names = []

        if model_path:
            self.load_model(model_path)

    def extract_features(self, task: Task, instance: Instance) -> np.ndarray:
        """Extract features for prediction

        Task Features:
        - Estimated LOC (lines of code)
        - Number of dependencies
        - Required skills count
        - Priority level
        - Task type (frontend/backend/test/etc)
        - Complexity score

        Instance Features:
        - Historical avg completion time
        - Current workload
        - Skill match score
        - Recent performance trend
        - Time of day (fatigue factor)

        Context Features:
        - Current system load
        - Pending tasks count
        - Recent failure rate
        """
        features = {
            # Task features
            'estimated_loc': task.estimated_hours * 50,  # rough estimate
            'num_dependencies': len(task.dependencies),
            'num_required_skills': len(task.required_skills),
            'priority': task.priority_score(),
            'is_frontend': 1 if 'frontend' in task.required_skills else 0,
            'is_backend': 1 if 'backend' in task.required_skills else 0,
            'is_testing': 1 if 'testing' in task.required_skills else 0,

            # Instance features
            'instance_avg_time': instance.stats.avg_completion_time,
            'instance_workload': len(instance.current_tasks),
            'skill_match_score': self._calculate_skill_match(task, instance),
            'instance_velocity': instance.stats.recent_velocity,
            'hour_of_day': datetime.now().hour,

            # System features
            'system_load': self._get_system_load(),
            'pending_tasks': self._get_pending_count(),
            'recent_failure_rate': self._get_failure_rate(),
        }

        self.feature_names = list(features.keys())
        return np.array(list(features.values())).reshape(1, -1)

    def predict_completion_time(self, task: Task, instance: Instance) -> Dict:
        """Predict task completion time with confidence interval"""
        features = self.extract_features(task, instance)
        features_scaled = self.scaler.transform(features)

        # Ensemble prediction
        predictions = [
            model.predict(features_scaled)[0]
            for model in self.models.values()
        ]

        mean_prediction = np.mean(predictions)
        std_prediction = np.std(predictions)

        return {
            'predicted_hours': mean_prediction,
            'confidence_interval': (
                mean_prediction - 1.96 * std_prediction,
                mean_prediction + 1.96 * std_prediction
            ),
            'confidence_score': 1.0 - (std_prediction / mean_prediction) if mean_prediction > 0 else 0.0
        }

    def predict_difficulty(self, task: Task) -> str:
        """Classify task difficulty: trivial, easy, medium, hard, expert"""
        # Use predicted time as proxy for difficulty
        # This could be a separate classification model
        pass

    def train(self, training_data: List[Dict]) -> Dict:
        """Train models on historical data

        training_data format:
        [
            {
                'task': Task,
                'instance': Instance,
                'actual_hours': float,
                'quality_score': float
            },
            ...
        ]
        """
        X = []
        y = []

        for record in training_data:
            features = self.extract_features(record['task'], record['instance'])
            X.append(features[0])
            y.append(record['actual_hours'])

        X = np.array(X)
        y = np.array(y)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train each model
        scores = {}
        for name, model in self.models.items():
            model.fit(X_scaled, y)
            scores[name] = model.score(X_scaled, y)

        return {
            'training_samples': len(training_data),
            'model_scores': scores,
            'feature_importance': self._get_feature_importance()
        }

    def update_model(self, actual_completion: Dict) -> None:
        """Incremental learning from new data"""
        # For online learning, could use SGDRegressor or partial_fit
        pass

    def save_model(self, path: str) -> None:
        """Persist trained models"""
        joblib.dump({
            'models': self.models,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, path)

    def load_model(self, path: str) -> None:
        """Load pre-trained models"""
        data = joblib.load(path)
        self.models = data['models']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
```

**Data Collection Pipeline** (`src/ml/data/collector.py`):
- Hooks into TechLeadSystem to record task assignments and completions
- Stores training data in PostgreSQL/BigQuery
- Automated daily retraining pipeline

**Evaluation Metrics**:
- Mean Absolute Error (MAE) < 1 hour
- R² score > 0.75
- Prediction accuracy improves over time

#### 2. Intelligent Instance Selection with Reinforcement Learning

**Problem**: Task assignment is a multi-objective optimization problem with delayed rewards.

**Solution**: Reinforcement Learning agent that learns optimal assignment policy.

**Implementation** (`src/ml/allocation/rl_allocator.py`):

```python
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random

class DQNNetwork(nn.Module):
    """Deep Q-Network for task allocation"""

    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )

    def forward(self, state):
        return self.network(state)

class SmartTaskAllocator:
    """RL-based task allocator using DQN"""

    def __init__(self, state_dim: int, max_instances: int = 10):
        self.state_dim = state_dim
        self.action_dim = max_instances

        # DQN components
        self.policy_net = DQNNetwork(state_dim, self.action_dim)
        self.target_net = DQNNetwork(state_dim, self.action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.memory = deque(maxlen=10000)

        # Hyperparameters
        self.gamma = 0.99  # discount factor
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 64

    def get_state(self, task: Task, instances: List[Instance]) -> torch.Tensor:
        """Encode current state as tensor

        State representation:
        - Task features (10 dimensions)
        - Each instance features (10 dimensions × max_instances)
        - Global system state (5 dimensions)
        """
        task_features = [
            task.estimated_hours,
            len(task.dependencies),
            len(task.required_skills),
            task.priority_score(),
            # ... more task features
        ]

        instance_features = []
        for i in range(self.action_dim):
            if i < len(instances):
                inst = instances[i]
                instance_features.extend([
                    len(inst.current_tasks),
                    inst.stats.avg_completion_time,
                    inst.stats.quality_score,
                    self._skill_match(task, inst),
                    # ... more instance features
                ])
            else:
                # Padding for unused instance slots
                instance_features.extend([0] * 10)

        system_features = [
            len([t for t in all_tasks if t.status == 'pending']),
            self._get_system_load(),
            # ... more system features
        ]

        state = task_features + instance_features + system_features
        return torch.FloatTensor(state)

    def select_best_instance(
        self,
        task: Task,
        instances: List[Instance],
        training: bool = False
    ) -> int:
        """Select instance using epsilon-greedy policy"""
        state = self.get_state(task, instances)

        # Exploration vs exploitation
        if training and random.random() < self.epsilon:
            # Random action (exploration)
            return random.randint(0, len(instances) - 1)
        else:
            # Best action according to policy (exploitation)
            with torch.no_grad():
                q_values = self.policy_net(state)
                # Mask unavailable instances
                available_mask = torch.tensor([
                    1.0 if i < len(instances) and instances[i].status == 'active' else -float('inf')
                    for i in range(self.action_dim)
                ])
                q_values = q_values + available_mask
                return q_values.argmax().item()

    def learn_from_outcome(
        self,
        state: torch.Tensor,
        action: int,
        reward: float,
        next_state: torch.Tensor,
        done: bool
    ) -> None:
        """Update Q-network from experience"""
        # Store experience in replay buffer
        self.memory.append((state, action, reward, next_state, done))

        if len(self.memory) < self.batch_size:
            return

        # Sample mini-batch
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.stack(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.stack(next_states)
        dones = torch.FloatTensor(dones)

        # Compute current Q values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1))

        # Compute target Q values
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        # Compute loss and update
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def calculate_reward(self, assignment_result: Dict) -> float:
        """Calculate reward for an assignment

        Reward components:
        - Negative completion time (faster is better)
        - Positive quality bonus
        - Negative resource cost
        - Bonus for meeting deadline
        """
        time_penalty = -assignment_result['completion_time'] / 10.0
        quality_bonus = assignment_result['quality_score'] * 2.0
        cost_penalty = -assignment_result['resource_cost'] / 100.0
        deadline_bonus = 5.0 if assignment_result['met_deadline'] else -3.0

        return time_penalty + quality_bonus + cost_penalty + deadline_bonus

    def update_target_network(self) -> None:
        """Periodically sync target network with policy network"""
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def save_model(self, path: str) -> None:
        """Save trained model"""
        torch.save({
            'policy_net': self.policy_net.state_dict(),
            'target_net': self.target_net.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, path)

    def load_model(self, path: str) -> None:
        """Load trained model"""
        checkpoint = torch.load(path)
        self.policy_net.load_state_dict(checkpoint['policy_net'])
        self.target_net.load_state_dict(checkpoint['target_net'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
```

**Training Strategy**:
1. **Offline Training**: Train on historical assignment data
2. **Online Learning**: Continuously learn from new assignments
3. **A/B Testing**: Compare RL policy vs rule-based allocation
4. **Safe Exploration**: Use epsilon-greedy with high initial epsilon in non-production

**Performance Targets**:
- 20% reduction in average task completion time
- 15% improvement in resource utilization
- 10% increase in quality scores

#### 3. Bottleneck Prediction & Prevention

**Problem**: Bottlenecks emerge unpredictably and disrupt development flow.

**Solution**: Time series forecasting to predict bottlenecks before they occur.

**Implementation** (`src/ml/forecasting/bottleneck_predictor.py`):

```python
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import pandas as pd

class BottleneckPredictor:
    """Predict system bottlenecks using time series analysis"""

    def __init__(self):
        self.models = {}
        self.history = defaultdict(list)

    def track_metric(self, metric_name: str, value: float, timestamp: datetime) -> None:
        """Record metric for time series analysis"""
        self.history[metric_name].append({
            'timestamp': timestamp,
            'value': value
        })

    def predict_bottlenecks(
        self,
        forecast_horizon: int = 24  # hours
    ) -> List[BottleneckPrediction]:
        """Forecast potential bottlenecks"""
        predictions = []

        # Analyze key metrics
        metrics_to_forecast = [
            'pending_tasks_count',
            'avg_instance_workload',
            'blocked_tasks_count',
            'avg_completion_time',
            'resource_utilization'
        ]

        for metric in metrics_to_forecast:
            forecast = self._forecast_metric(metric, forecast_horizon)

            # Check if forecast exceeds threshold
            threshold = self._get_threshold(metric)
            if any(val > threshold for val in forecast['values']):
                predictions.append(BottleneckPrediction(
                    metric=metric,
                    predicted_peak=max(forecast['values']),
                    time_to_peak=forecast['time_to_peak'],
                    confidence=forecast['confidence'],
                    recommended_actions=self._get_recommended_actions(metric)
                ))

        return predictions

    def _forecast_metric(self, metric: str, hours: int) -> Dict:
        """Forecast a single metric using Prophet"""
        # Prepare data
        df = pd.DataFrame(self.history[metric])
        df.columns = ['ds', 'y']

        # Train Prophet model
        model = Prophet(
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
            daily_seasonality=True,
            weekly_seasonality=True
        )
        model.fit(df)

        # Make forecast
        future = model.make_future_dataframe(periods=hours, freq='H')
        forecast = model.predict(future)

        # Extract predictions
        future_forecast = forecast.tail(hours)

        return {
            'values': future_forecast['yhat'].values,
            'time_to_peak': future_forecast['yhat'].idxmax(),
            'confidence': 1.0 - (future_forecast['yhat_upper'] - future_forecast['yhat_lower']).mean() / future_forecast['yhat'].mean()
        }

    def recommend_preventive_actions(
        self,
        bottleneck: BottleneckPrediction
    ) -> List[Action]:
        """Generate preventive actions for predicted bottleneck"""
        actions = []

        if bottleneck.metric == 'pending_tasks_count':
            actions.append(Action(
                type='scale_instances',
                description='Add 2 more Claude Code instances',
                estimated_impact='Reduce pending queue by 40%'
            ))

        elif bottleneck.metric == 'avg_instance_workload':
            actions.append(Action(
                type='redistribute_tasks',
                description='Rebalance tasks across instances',
                estimated_impact='Even out workload distribution'
            ))

        elif bottleneck.metric == 'blocked_tasks_count':
            actions.append(Action(
                type='prioritize_blockers',
                description='Auto-prioritize dependency tasks',
                estimated_impact='Unblock 60% of blocked tasks'
            ))

        return actions
```

**Integration with NotificationHub**:
- Send early warning alerts 2-4 hours before predicted bottleneck
- Provide actionable recommendations
- Auto-trigger preventive actions if confidence > 80%

#### 4. MLOps Infrastructure

**Experiment Tracking** (MLflow):
```python
import mlflow

def train_model_with_tracking(training_data):
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("model_type", "random_forest")
        mlflow.log_param("n_estimators", 100)

        # Train model
        model = train_model(training_data)

        # Log metrics
        mlflow.log_metric("mae", calculate_mae(model))
        mlflow.log_metric("r2_score", calculate_r2(model))

        # Log model
        mlflow.sklearn.log_model(model, "model")
```

**Model Serving** (FastAPI):
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictionRequest(BaseModel):
    task_id: str
    instance_id: int

@app.post("/predict/completion-time")
async def predict_completion_time(request: PredictionRequest):
    task = get_task(request.task_id)
    instance = get_instance(request.instance_id)

    prediction = predictor.predict_completion_time(task, instance)
    return prediction
```

**Continuous Training Pipeline**:
1. Daily batch retraining with new data
2. A/B testing of model versions
3. Gradual rollout of new models
4. Automatic rollback if performance degrades

### Deliverables

**Code**:
- `src/ml/prediction/task_predictor.py` (500 lines)
- `src/ml/allocation/rl_allocator.py` (600 lines)
- `src/ml/forecasting/bottleneck_predictor.py` (400 lines)
- `src/ml/data/collector.py` (300 lines)
- `src/ml/serving/api.py` (200 lines)
- `src/ml/training/pipeline.py` (300 lines)

**Infrastructure**:
- MLflow experiment tracking
- Model registry (Vertex AI / MLflow)
- Training pipelines (Airflow / Vertex AI Pipelines)
- Model serving endpoints

**Documentation**:
- ML model documentation
- Training procedures
- Model performance monitoring
- A/B testing results

### Success Metrics

- [ ] Task completion time prediction accuracy > 80%
- [ ] 20% improvement in task allocation efficiency
- [ ] 50% reduction in bottleneck incidents
- [ ] Models automatically retrain daily
- [ ] A/B testing shows significant improvement over rule-based

### Technical Stack

- **ML**: scikit-learn, TensorFlow, PyTorch, Prophet
- **MLOps**: MLflow, Vertex AI, Airflow
- **Data**: PostgreSQL, BigQuery, Apache Arrow
- **Serving**: FastAPI, gRPC
- **Monitoring**: Prometheus, Grafana

### Timeline

**Week 11**:
- Data collection pipeline
- Task completion predictor
- Initial model training

**Week 12**:
- RL-based instance selector
- Bottleneck forecasting
- Integration with TechLeadSystem

**Week 13**:
- MLOps infrastructure
- A/B testing framework
- Performance evaluation

---

## 🎨 Phase 7: Real-time Collaboration UI

**Duration**: Week 14-16 (3 weeks)
**Goal**: Build interactive web interface for real-time monitoring and control of autonomous development

### Motivation

Current system is command-line driven with limited visibility into real-time operations. Human developers need:
- Visual understanding of what instances are doing
- Ability to intervene when necessary
- Real-time collaboration with AI instances
- Transparent decision-making process

### Detailed Components

#### 1. Real-time Dashboard Architecture

**Frontend Stack**:
- React 18 with TypeScript
- TailwindCSS for styling
- shadcn/ui component library
- React Query for state management
- WebSocket for real-time updates

**Backend API Gateway** (`backend/api/gateway.py`):
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send updates every second
            update = await get_system_state()
            await websocket.send_json(update)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def get_system_state() -> dict:
    """Aggregate current system state"""
    return {
        'instances': [
            {
                'id': inst.instance_id,
                'name': inst.name,
                'status': inst.status,
                'current_tasks': inst.current_tasks,
                'workload': len(inst.current_tasks),
                'performance': inst.stats.quality_score
            }
            for inst in manager.instances.values()
        ],
        'tasks': [
            {
                'id': task.task_id,
                'title': task.title,
                'status': task.status,
                'assigned_to': task.assigned_to,
                'progress': task.progress_percentage
            }
            for task in manager.tasks.values()
        ],
        'alerts': notification_hub.get_active_alerts(),
        'metrics': {
            'velocity': tech_lead.generate_progress_report().velocity,
            'completion_rate': tech_lead.generate_progress_report().overall_completion,
            'bottlenecks': len(tech_lead.detect_bottlenecks())
        }
    }
```

**Frontend Real-time Hook** (`frontend/src/hooks/useRealtimeUpdates.ts`):
```typescript
import { useState, useEffect } from 'react'
import { Instance, Task, Alert } from '@/types'

interface SystemState {
  instances: Instance[]
  tasks: Task[]
  alerts: Alert[]
  metrics: {
    velocity: number
    completion_rate: number
    bottlenecks: number
  }
}

export const useRealtimeUpdates = () => {
  const [state, setState] = useState<SystemState | null>(null)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/realtime')

    ws.onopen = () => {
      setConnected(true)
      setError(null)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setState(data)
    }

    ws.onerror = (error) => {
      setError('WebSocket connection failed')
      setConnected(false)
    }

    ws.onclose = () => {
      setConnected(false)
      // Attempt reconnection after 5 seconds
      setTimeout(() => {
        // Reconnect logic
      }, 5000)
    }

    return () => {
      ws.close()
    }
  }, [])

  return { state, connected, error }
}
```

#### 2. Interactive Visualizations

**Instance Network Graph** (`frontend/src/components/InstanceNetwork.tsx`):
```typescript
import React from 'react'
import { ForceGraph2D } from 'react-force-graph'

interface InstanceNetworkProps {
  instances: Instance[]
  messages: Message[]
}

export const InstanceNetwork: React.FC<InstanceNetworkProps> = ({
  instances,
  messages
}) => {
  // Transform instances into nodes
  const nodes = instances.map(inst => ({
    id: inst.id,
    name: inst.name,
    val: inst.workload, // Node size based on workload
    color: getStatusColor(inst.status)
  }))

  // Transform messages into links
  const links = messages.map(msg => ({
    source: msg.sender_id,
    target: msg.receiver_id,
    value: msg.importance
  }))

  const graphData = { nodes, links }

  return (
    <div className="w-full h-[600px]">
      <ForceGraph2D
        graphData={graphData}
        nodeLabel="name"
        nodeAutoColorBy="color"
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        onNodeClick={handleNodeClick}
      />
    </div>
  )
}
```

**Task Timeline Gantt Chart** (`frontend/src/components/TaskTimeline.tsx`):
{% raw %}
```typescript
import React from 'react'
import { Chart } from 'react-google-charts'

export const TaskTimeline: React.FC<{ tasks: Task[] }> = ({ tasks }) => {
  const data = [
    [
      { type: 'string', label: 'Task ID' },
      { type: 'string', label: 'Task Name' },
      { type: 'string', label: 'Resource' },
      { type: 'date', label: 'Start' },
      { type: 'date', label: 'End' },
      { type: 'number', label: 'Duration' },
      { type: 'number', label: 'Percent Complete' },
      { type: 'string', label: 'Dependencies' },
    ],
    ...tasks.map(task => [
      task.id,
      task.title,
      `Instance ${task.assigned_to}`,
      new Date(task.started_at),
      new Date(task.estimated_completion),
      null,
      task.progress_percentage,
      task.dependencies.join(',')
    ])
  ]

  return (
    <Chart
      chartType="Gantt"
      width="100%"
      height="400px"
      data={data}
      options={{
        gantt: {
          criticalPathEnabled: true,
          criticalPathStyle: {
            stroke: '#e74c3c',
            strokeWidth: 5,
          },
        },
      }}
    />
  )
}
```
{% endraw %}

#### 3. Interactive Controls

**Drag-and-Drop Task Reassignment** (`frontend/src/components/TaskBoard.tsx`):
```typescript
import React from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'

export const TaskBoard: React.FC<{ instances: Instance[] }> = ({ instances }) => {
  const handleDragEnd = async (result) => {
    if (!result.destination) return

    const taskId = result.draggableId
    const newInstanceId = parseInt(result.destination.droppableId)

    // Call API to reassign task
    await fetch('/api/tasks/reassign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId, instance_id: newInstanceId })
    })

    // Optimistic UI update handled by React Query
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="flex gap-4">
        {instances.map(instance => (
          <Droppable key={instance.id} droppableId={String(instance.id)}>
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="bg-gray-100 p-4 rounded-lg min-w-[300px]"
              >
                <h3 className="font-bold mb-4">{instance.name}</h3>
                {instance.tasks.map((task, index) => (
                  <Draggable
                    key={task.id}
                    draggableId={task.id}
                    index={index}
                  >
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className="bg-white p-3 mb-2 rounded shadow"
                      >
                        {task.title}
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  )
}
```

**Instance Control Panel** (`frontend/src/components/InstanceControls.tsx`):
```typescript
import React from 'react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'

export const InstanceControls: React.FC<{ instance: Instance }> = ({ instance }) => {
  const handlePause = async () => {
    await fetch(`/api/instances/${instance.id}/pause`, { method: 'POST' })
  }

  const handleResume = async () => {
    await fetch(`/api/instances/${instance.id}/resume`, { method: 'POST' })
  }

  const handleResourceLimitChange = async (value: number[]) => {
    await fetch(`/api/instances/${instance.id}/resources`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ max_concurrent_tasks: value[0] })
    })
  }

  return (
    <div className="space-y-4 p-4 border rounded-lg">
      <div className="flex gap-2">
        <Button
          onClick={handlePause}
          disabled={instance.status !== 'active'}
        >
          Pause
        </Button>
        <Button
          onClick={handleResume}
          disabled={instance.status === 'active'}
        >
          Resume
        </Button>
      </div>

      <div>
        <label className="text-sm font-medium">Max Concurrent Tasks</label>
        <Slider
          value={[instance.max_concurrent_tasks]}
          min={1}
          max={10}
          step={1}
          onValueCommit={handleResourceLimitChange}
        />
      </div>

      <div className="text-sm text-gray-600">
        Current: {instance.current_tasks.length} / {instance.max_concurrent_tasks}
      </div>
    </div>
  )
}
```

#### 4. Knowledge Base Browser

**Project Memory UI** (`frontend/src/components/KnowledgeBase.tsx`):
```typescript
import React, { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [entries, setEntries] = useState([])

  const handleSearch = async (query: string) => {
    const response = await fetch(`/api/memory/search?q=${encodeURIComponent(query)}`)
    const results = await response.json()
    setEntries(results)
  }

  return (
    <div className="p-6">
      <Input
        placeholder="Search knowledge base..."
        value={searchQuery}
        onChange={(e) => {
          setSearchQuery(e.target.value)
          handleSearch(e.target.value)
        }}
      />

      <Tabs defaultValue="all" className="mt-4">
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="decisions">Decisions</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
          <TabsTrigger value="learnings">Learnings</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {entries.map(entry => (
            <div key={entry.id} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold">{entry.title}</h3>
                <span className="text-sm text-gray-500">{entry.knowledge_type}</span>
              </div>
              <p className="text-gray-700">{entry.content}</p>
              <div className="mt-2 flex gap-2">
                {entry.tags.map(tag => (
                  <span key={tag} className="text-xs bg-gray-200 px-2 py-1 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### Deliverables

**Frontend**:
- React application with TypeScript (~2,500 lines)
- Component library (~1,000 lines)
- Real-time visualization (~500 lines)

**Backend**:
- FastAPI gateway (~800 lines)
- WebSocket server (~400 lines)
- REST API endpoints (~600 lines)

**Infrastructure**:
- Frontend deployment (Vercel/Netlify)
- Backend deployment (Cloud Run)
- CDN setup

### Success Metrics

- [ ] <100ms WebSocket latency
- [ ] Support 100+ concurrent users
- [ ] Mobile responsive (tested on iOS/Android)
- [ ] 99.9% uptime
- [ ] WCAG 2.1 AA accessibility compliance

### Timeline

**Week 14**:
- React app setup
- WebSocket infrastructure
- Basic dashboard layout
- Instance visualization

**Week 15**:
- Interactive controls
- Drag-and-drop task board
- Knowledge base browser
- Alert dashboard

**Week 16**:
- Polish and animations
- Mobile responsiveness
- Performance optimization
- User acceptance testing

---

## 🌐 Phase 8: Cross-Repository Collaboration

**Duration**: Week 17-20 (4 weeks)
**Goal**: Enable autonomous development across multiple repositories with intelligent coordination

### Motivation

Modern software systems consist of multiple repositories:
- Microservices architecture
- Shared libraries
- Frontend/backend separation
- Multi-tenant systems

Current system is limited to single-repository operation. Cross-repo collaboration enables:
- Coordinated changes across service boundaries
- API contract evolution
- Dependency management
- Distributed testing

### Detailed Components

#### 1. Multi-Repository Coordinator

**Repository Discovery** (`src/cross_repo/discovery.py`):
```python
import git
import requests
from typing import List, Dict

class RepositoryDiscovery:
    """Discover and map repository dependencies"""

    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.dependency_graph = nx.DiGraph()

    def discover_organization_repos(self, org_name: str) -> List[Repository]:
        """Find all repositories in an organization"""
        org = self.github.get_organization(org_name)
        return list(org.get_repos())

    def analyze_dependencies(self, repo: Repository) -> List[Dependency]:
        """Analyze repository dependencies

        Checks:
        - package.json (Node.js)
        - requirements.txt (Python)
        - go.mod (Go)
        - build.gradle (Java)
        - API calls in code
        """
        dependencies = []

        # Language-specific dependency analysis
        if self._has_file(repo, 'package.json'):
            dependencies.extend(self._analyze_npm_dependencies(repo))

        if self._has_file(repo, 'requirements.txt'):
            dependencies.extend(self._analyze_python_dependencies(repo))

        # API dependency analysis
        dependencies.extend(self._analyze_api_calls(repo))

        return dependencies

    def build_dependency_graph(self, repos: List[Repository]) -> nx.DiGraph:
        """Build graph of repository dependencies"""
        for repo in repos:
            self.dependency_graph.add_node(repo.name, repo=repo)

            deps = self.analyze_dependencies(repo)
            for dep in deps:
                if dep.repo_name in [r.name for r in repos]:
                    self.dependency_graph.add_edge(
                        repo.name,
                        dep.repo_name,
                        dependency_type=dep.type
                    )

        return self.dependency_graph

    def find_affected_repos(self, changed_repo: str) -> List[str]:
        """Find all repos affected by a change in given repo"""
        # Use DFS to find all downstream dependencies
        return list(nx.descendants(self.dependency_graph, changed_repo))
```

**Cross-Repo Coordinator** (`src/cross_repo/coordinator.py`):
```python
class CrossRepoCoordinator:
    """Coordinate development across multiple repositories"""

    def __init__(self, repos: List[Repository]):
        self.repos = {repo.name: repo for repo in repos}
        self.discovery = RepositoryDiscovery(github_token)
        self.dependency_graph = self.discovery.build_dependency_graph(repos)
        self.memory = UnifiedKnowledgeBase()

    def coordinate_change(self, change: Change) -> CoordinationPlan:
        """Create coordination plan for a change

        Example: API endpoint modification
        1. Identify affected repos
        2. Determine update order (topological sort)
        3. Create tasks for each repo
        4. Coordinate testing
        5. Plan deployment
        """
        source_repo = change.repository
        affected_repos = self.discovery.find_affected_repos(source_repo)

        # Topological sort for update order
        update_order = list(nx.topological_sort(
            self.dependency_graph.subgraph([source_repo] + affected_repos)
        ))

        plan = CoordinationPlan(
            change=change,
            affected_repositories=affected_repos,
            update_order=update_order,
            tasks=[]
        )

        # Create tasks for each repository
        for repo_name in update_order:
            tasks = self._create_repo_tasks(repo_name, change)
            plan.tasks.extend(tasks)

        return plan

    def _create_repo_tasks(self, repo_name: str, change: Change) -> List[Task]:
        """Generate tasks for repository update"""
        tasks = []

        if repo_name == change.repository:
            # Source repository tasks
            tasks.append(Task(
                title=f"Implement change in {repo_name}",
                description=change.description,
                repository=repo_name
            ))
        else:
            # Dependent repository tasks
            tasks.append(Task(
                title=f"Update {repo_name} for API change",
                description=f"Adapt to changes in {change.repository}",
                repository=repo_name,
                dependencies=[f"{change.repository}-implementation"]
            ))

        # Add integration test task
        tasks.append(Task(
            title=f"Integration test for {repo_name}",
            description="Run cross-repo integration tests",
            repository=repo_name,
            task_type="testing"
        ))

        return tasks

    def execute_coordinated_change(self, plan: CoordinationPlan) -> Result:
        """Execute coordination plan across repositories"""
        results = []

        for task in plan.tasks:
            # Assign to appropriate instance based on repository
            instance = self._select_instance_for_repo(task.repository)

            # Execute task
            result = await instance.execute(task)
            results.append(result)

            # Update shared knowledge
            self.memory.record_change(task.repository, result)

        return CoordinationResult(
            plan=plan,
            task_results=results,
            overall_success=all(r.success for r in results)
        )
```

#### 2. API Contract Management

**Contract Tracking** (`src/cross_repo/contracts.py`):
```python
from openapi_spec_validator import validate_spec
import yaml

class APIContractManager:
    """Manage API contracts across repositories"""

    def __init__(self):
        self.contracts = {}
        self.versions = defaultdict(list)

    def register_api(self, repo: str, openapi_spec: dict) -> None:
        """Register API specification"""
        # Validate OpenAPI spec
        validate_spec(openapi_spec)

        version = openapi_spec['info']['version']
        self.contracts[repo] = openapi_spec
        self.versions[repo].append({
            'version': version,
            'spec': openapi_spec,
            'registered_at': datetime.now()
        })

    def detect_breaking_changes(
        self,
        repo: str,
        new_spec: dict
    ) -> List[BreakingChange]:
        """Detect breaking changes in API"""
        old_spec = self.contracts.get(repo)
        if not old_spec:
            return []

        breaking_changes = []

        # Check for removed endpoints
        old_paths = set(old_spec['paths'].keys())
        new_paths = set(new_spec['paths'].keys())
        removed_paths = old_paths - new_paths

        for path in removed_paths:
            breaking_changes.append(BreakingChange(
                type='endpoint_removed',
                path=path,
                severity='high',
                message=f"Endpoint {path} was removed"
            ))

        # Check for parameter changes
        for path in old_paths & new_paths:
            for method in old_spec['paths'][path]:
                if method not in new_spec['paths'][path]:
                    breaking_changes.append(BreakingChange(
                        type='method_removed',
                        path=path,
                        method=method,
                        severity='high'
                    ))

        return breaking_changes

    def generate_migration_guide(
        self,
        repo: str,
        old_version: str,
        new_version: str
    ) -> str:
        """Auto-generate migration guide for API changes"""
        old_spec = self._get_spec_version(repo, old_version)
        new_spec = self._get_spec_version(repo, new_version)

        breaking_changes = self.detect_breaking_changes(repo, new_spec)

        guide = f"# Migration Guide: {repo} {old_version} → {new_version}\n\n"
        guide += "## Breaking Changes\n\n"

        for change in breaking_changes:
            guide += f"### {change.type}: {change.path}\n"
            guide += f"**Severity**: {change.severity}\n\n"
            guide += f"{change.message}\n\n"
            guide += "**Migration steps**:\n"
            guide += self._generate_migration_steps(change) + "\n\n"

        return guide
```

#### 3. Distributed Testing

**Cross-Repo Test Orchestrator** (`src/cross_repo/testing.py`):
```python
class CrossRepoTestOrchestrator:
    """Orchestrate testing across multiple repositories"""

    def __init__(self, repos: List[Repository]):
        self.repos = repos
        self.contract_tester = ContractTester()

    async def run_integration_tests(
        self,
        changed_repos: List[str]
    ) -> TestResults:
        """Run integration tests across affected repositories"""
        # Start services
        services = await self._start_test_services(changed_repos)

        try:
            results = []

            # Run contract tests
            for repo in changed_repos:
                contract_results = await self.contract_tester.verify_contracts(
                    provider=repo,
                    consumers=self._get_consumers(repo)
                )
                results.extend(contract_results)

            # Run end-to-end scenarios
            e2e_results = await self._run_e2e_scenarios(changed_repos)
            results.extend(e2e_results)

            return TestResults(
                total_tests=len(results),
                passed=[r for r in results if r.passed],
                failed=[r for r in results if not r.passed]
            )

        finally:
            # Cleanup test services
            await self._cleanup_services(services)

    async def _start_test_services(
        self,
        repos: List[str]
    ) -> List[Service]:
        """Start test instances of services"""
        services = []

        for repo in repos:
            # Use docker-compose or k8s for test environment
            service = await self._deploy_test_instance(repo)
            services.append(service)

        # Wait for all services to be healthy
        await self._wait_for_health(services)

        return services
```

**Contract Testing with Pact** (`src/cross_repo/pact_testing.py`):
```python
from pact import Consumer, Provider

class ContractTester:
    """Contract testing using Pact"""

    def __init__(self):
        self.pact_broker_url = "https://pact-broker.example.com"

    async def verify_contracts(
        self,
        provider: str,
        consumers: List[str]
    ) -> List[ContractTestResult]:
        """Verify provider meets consumer contracts"""
        results = []

        for consumer in consumers:
            # Fetch contract from Pact Broker
            contract = await self._fetch_contract(consumer, provider)

            # Verify provider against contract
            result = await self._verify_provider(provider, contract)
            results.append(result)

        return results
```

### Deliverables

**Code**:
- `src/cross_repo/discovery.py` (400 lines)
- `src/cross_repo/coordinator.py` (600 lines)
- `src/cross_repo/contracts.py` (500 lines)
- `src/cross_repo/testing.py` (700 lines)
- `src/cross_repo/unified_memory.py` (400 lines)

**Infrastructure**:
- Service mesh (Istio) configuration
- Distributed tracing (Jaeger)
- Pact broker setup
- Multi-repo CI/CD

**Documentation**:
- Cross-repo development guide
- API evolution strategy
- Contract testing guide

### Success Metrics

- [ ] Support 10+ repositories
- [ ] Automatic dependency discovery
- [ ] <5 minute change propagation
- [ ] 100% API contract coverage
- [ ] Zero breaking changes reaching production

### Timeline

**Week 17**:
- Repository discovery
- Dependency graph analysis
- Multi-repo coordinator

**Week 18**:
- API contract management
- Breaking change detection
- Migration guide generation

**Week 19**:
- Contract testing setup
- Integration test orchestration
- Service mesh integration

**Week 20**:
- End-to-end testing
- Performance optimization
- Production readiness

---

## 📊 Overall Extended Roadmap

### Timeline Summary

```
Phase 1-3: ████████████████ Week 1-6   (Completed)
Phase 4-5: ░░░░░░░░░░░░░░░░ Week 7-10  (Next)
Phase 6:   ░░░░░░░░░░░░░░░░ Week 11-13 (ML Optimization)
Phase 7:   ░░░░░░░░░░░░░░░░ Week 14-16 (Realtime UI)
Phase 8:   ░░░░░░░░░░░░░░░░ Week 17-20 (Cross-Repo)
```

### Total Effort Estimation

| Component | Estimated Lines | Person-Weeks |
|-----------|----------------|--------------|
| Phase 6: ML | 3,000+ | 3 |
| Phase 7: UI | 4,000+ | 3 |
| Phase 8: Cross-Repo | 5,000+ | 4 |
| **Total** | **12,000+** | **10** |

### Dependencies

```
Phase 1-5 (Core) → Phase 6 (ML) → Phase 7 (UI)
                                ↘ Phase 8 (Cross-Repo)
```

- Phase 6 can start immediately after Phase 5
- Phase 7 requires Phase 6 data (for ML-powered insights in UI)
- Phase 8 is independent and can run in parallel with Phase 7

### Key Decision Points

#### After Phase 5 (Week 10)
**Decision**: Proceed with Phase 6 (ML) or Phase 8 (Cross-Repo) first?

**Recommendation**: Phase 6 (ML)
- Provides immediate value to existing system
- Data collection can start early
- Easier to implement and test
- Enables better Phase 7 (UI) with ML insights

#### After Phase 7 (Week 16)
**Decision**: Invest in Phase 8 (Cross-Repo) or focus on production optimization?

**Factors to consider**:
- Is the system being used for multi-repo projects?
- Is there demand for microservices support?
- Are resources available for 4-week development?

---

## 🎯 Success Criteria

### Phase 6 Success Metrics
- [ ] >80% prediction accuracy for task completion times
- [ ] 20% reduction in average completion time (via better allocation)
- [ ] 50% reduction in bottleneck incidents
- [ ] Models retrain automatically
- [ ] ML insights visible in dashboard

### Phase 7 Success Metrics
- [ ] <100ms WebSocket latency
- [ ] Support 100+ concurrent users
- [ ] Mobile-responsive design
- [ ] 99.9% UI uptime
- [ ] Positive user feedback (>4/5 rating)

### Phase 8 Success Metrics
- [ ] Support 10+ repositories seamlessly
- [ ] Automatic dependency resolution
- [ ] <5 minute cross-repo change propagation
- [ ] 100% API contract coverage
- [ ] Zero production breaking changes

---

## 🚀 Getting Started (After Phase 5)

### Phase 6 Prerequisites

1. **Data Collection Setup**:
   ```bash
   # Create tables for ML training data
   python scripts/setup_ml_database.py

   # Start data collection
   python src/ml/data/collector.py --mode=continuous
   ```

2. **Initial Model Training**:
   ```bash
   # Train baseline models
   python src/ml/training/train_initial.py
   ```

3. **MLOps Infrastructure**:
   ```bash
   # Setup MLflow
   mlflow server --backend-store-uri postgresql://... --default-artifact-root gs://...
   ```

### Phase 7 Prerequisites

1. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **API Gateway**:
   ```bash
   cd backend
   uvicorn api.gateway:app --reload
   ```

### Phase 8 Prerequisites

1. **Multi-Repo Setup**:
   ```bash
   # Clone all repositories
   python scripts/setup_multi_repo.py --org=your-org
   ```

2. **Service Mesh**:
   ```bash
   istioctl install --set profile=demo
   ```

---

## 📞 Support & Resources

- **GitHub Issues**: Track Phase 6-8 development
- **Documentation**: Extended roadmap updates in `/docs`
- **Slack**: #ml-optimization, #realtime-ui, #cross-repo channels

---

**Last Updated**: 2025-11-01
**Status**: Planning Phase - Awaiting Phase 5 Completion
**Next Review**: After Phase 5 completion
