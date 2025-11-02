package github

import (
	"bufio"
	"context"
	"fmt"
	"net/http"
	"strings"

	"github.com/google/go-github/v56/github"
)

// GetWorkflowLogs gets logs for a workflow run
func (c *Client) GetWorkflowLogs(runID int64) (string, error) {
	// Get logs URL
	url, _, err := c.client.Actions.GetWorkflowRunLogs(c.ctx, c.owner, c.repo, runID, true)
	if err != nil {
		return "", fmt.Errorf("failed to get logs URL: %w", err)
	}

	// Download logs
	req, err := http.NewRequest("GET", url.String(), nil)
	if err != nil {
		return "", err
	}

	httpClient := &http.Client{}
	resp, err := httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	// Parse logs
	var logs strings.Builder
	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		logs.WriteString(scanner.Text())
		logs.WriteString("\n")
	}

	return logs.String(), scanner.Err()
}

// StreamWorkflowLogs streams logs in real-time (polling)
func (c *Client) StreamWorkflowLogs(runID int64, callback func(string)) error {
	// GitHub doesn't support true streaming, so we poll
	// In production, use websockets or SSE for real-time updates

	logs, err := c.GetWorkflowLogs(runID)
	if err != nil {
		return err
	}

	callback(logs)
	return nil
}

// GetJobLogs gets logs for a specific job
func (c *Client) GetJobLogs(jobID int64) (string, error) {
	logs, _, err := c.client.Actions.GetWorkflowJobLogs(c.ctx, c.owner, c.repo, jobID, true)
	if err != nil {
		return "", fmt.Errorf("failed to get job logs: %w", err)
	}

	return logs.String(), nil
}
