package github

import (
	"context"
	"fmt"

	"github.com/google/go-github/v56/github"
	"golang.org/x/oauth2"
)

// Client wraps GitHub API client
type Client struct {
	client *github.Client
	owner  string
	repo   string
	ctx    context.Context
}

// Issue represents a GitHub issue
type Issue struct {
	Number int
	Title  string
	URL    string
}

// WorkflowRun represents a workflow run
type WorkflowRun struct {
	ID        int64
	Status    string
	URL       string
	CreatedAt string
}

// Job represents a workflow job
type Job struct {
	Name   string
	Status string
}

// NewClient creates a new GitHub client
func NewClient(token, owner, repo string) *Client {
	ctx := context.Background()
	ts := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: token},
	)
	tc := oauth2.NewClient(ctx, ts)

	return &Client{
		client: github.NewClient(tc),
		owner:  owner,
		repo:   repo,
		ctx:    ctx,
	}
}

// CreateIssue creates a new GitHub issue
func (c *Client) CreateIssue(title, body string) (*Issue, error) {
	issueReq := &github.IssueRequest{
		Title:  &title,
		Body:   &body,
		Labels: &[]string{"autonomous-dev"},
	}

	issue, _, err := c.client.Issues.Create(c.ctx, c.owner, c.repo, issueReq)
	if err != nil {
		return nil, fmt.Errorf("failed to create issue: %w", err)
	}

	return &Issue{
		Number: *issue.Number,
		Title:  *issue.Title,
		URL:    *issue.HTMLURL,
	}, nil
}

// TriggerWorkflow triggers the autonomous-dev workflow
func (c *Client) TriggerWorkflow(issueNumber, instances int) (*WorkflowRun, error) {
	workflowFile := "autonomous-dev.yml"

	// Create workflow dispatch event
	dispatchReq := github.CreateWorkflowDispatchEventRequest{
		Ref: "main",
		Inputs: map[string]interface{}{
			"issue_number":   fmt.Sprint(issueNumber),
			"instance_count": fmt.Sprint(instances),
		},
	}

	_, err := c.client.Actions.CreateWorkflowDispatchEventByFileName(
		c.ctx,
		c.owner,
		c.repo,
		workflowFile,
		dispatchReq,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to trigger workflow: %w", err)
	}

	// Get the latest workflow run (just triggered)
	// Note: There's a small delay, so we return a placeholder
	run := &WorkflowRun{
		ID:     0, // Will be set when we query
		Status: "queued",
		URL:    fmt.Sprintf("https://github.com/%s/%s/actions", c.owner, c.repo),
	}

	return run, nil
}

// GetLatestWorkflowRun gets the latest autonomous-dev workflow run
func (c *Client) GetLatestWorkflowRun() (*WorkflowRun, error) {
	opts := &github.ListWorkflowRunsOptions{
		ListOptions: github.ListOptions{
			PerPage: 1,
		},
	}

	runs, _, err := c.client.Actions.ListWorkflowRunsByFileName(
		c.ctx,
		c.owner,
		c.repo,
		"autonomous-dev.yml",
		opts,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to list workflow runs: %w", err)
	}

	if len(runs.WorkflowRuns) == 0 {
		return nil, nil
	}

	run := runs.WorkflowRuns[0]
	return &WorkflowRun{
		ID:        *run.ID,
		Status:    *run.Status,
		URL:       *run.HTMLURL,
		CreatedAt: run.CreatedAt.String(),
	}, nil
}

// GetWorkflowJobs gets jobs for a workflow run
func (c *Client) GetWorkflowJobs(runID int64) ([]Job, error) {
	opts := &github.ListWorkflowJobsOptions{
		ListOptions: github.ListOptions{
			PerPage: 100,
		},
	}

	jobs, _, err := c.client.Actions.ListWorkflowJobs(
		c.ctx,
		c.owner,
		c.repo,
		runID,
		opts,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to list workflow jobs: %w", err)
	}

	result := make([]Job, 0, len(jobs.Jobs))
	for _, job := range jobs.Jobs {
		result = append(result, Job{
			Name:   *job.Name,
			Status: *job.Status,
		})
	}

	return result, nil
}
