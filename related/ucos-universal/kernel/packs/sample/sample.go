// Package sample implements the Phase 0 exit-test pack `sample.notes` (U57 Appendix S) on the Pack SDK.
// It touches every kernel path: objects with versions, lifecycle rules, policy-style checks, events,
// a scheduled reminder through the trigger engine, and audit (written by the bus).
package sample

import (
	"encoding/json"
	"net/http"
	"slices"
	"strings"

	"ucos.io/kernel/sdk/pack"
)

const noteType = "ucos.sample.Note"

// Note mirrors spec/object-types/ucos.sample.Note.schema.json.
type Note struct {
	Title       map[string]string `json:"title"`
	Body        string            `json:"body"`
	Author      string            `json:"author"`
	RemindAt    string            `json:"remindAt,omitempty"`
	PublishedAt string            `json:"publishedAt,omitempty"`
	Tags        []string          `json:"tags"`
}

type Pack struct{}

func (Pack) CapabilityID() string { return "sample.notes" }

func (p Pack) Commands() map[string]pack.CommandHandler {
	return map[string]pack.CommandHandler{
		"CreateNote": p.create, "EditNote": p.edit, "PublishNote": p.publish, "ArchiveNote": p.archive,
		"ScheduleNoteReminder": p.schedule, "RemindNote": p.remind,
	}
}
func (p Pack) Queries() map[string]pack.QueryHandler {
	return map[string]pack.QueryHandler{"GetNote": p.get, "ListNotes": p.list}
}
func (Pack) Events() map[string]pack.EventHandler { return map[string]pack.EventHandler{} }

type input struct {
	Target string            `json:"_target"`
	Title  map[string]string `json:"title"`
	Body   string            `json:"body"`
	Tags   []string          `json:"tags"`
	At     string            `json:"at"`
}

func bad(code, title string) error {
	return pack.NewProblem(http.StatusUnprocessableEntity, code, title, "")
}

func parse(raw json.RawMessage) (input, error) {
	var in input
	if len(raw) > 0 {
		if err := json.Unmarshal(raw, &in); err != nil {
			return in, pack.NewProblem(http.StatusBadRequest, "SAMPLE_INVALID_INPUT", "payload is not valid JSON", err.Error())
		}
	}
	return in, nil
}

func load(c *pack.CommandCtx, id string) (*pack.Object, Note, error) {
	o, err := c.Tx.Get(noteType, id)
	if err != nil {
		return nil, Note{}, err
	}
	var n Note
	if err := json.Unmarshal(o.Attributes, &n); err != nil {
		return nil, Note{}, err
	}
	return o, n, nil
}

func save(c *pack.CommandCtx, o *pack.Object, n Note, expected int64) error {
	a, err := json.Marshal(n)
	if err != nil {
		return err
	}
	o.Attributes = a
	return c.Tx.Save(o, expected)
}

func (Pack) create(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	in, err := parse(raw)
	if err != nil {
		return pack.Result{}, err
	}
	if strings.TrimSpace(in.Title["en"]) == "" && len(in.Title) == 0 {
		return pack.Result{}, bad("SAMPLE_TITLE_REQUIRED", "a title is required")
	}
	id, err := c.Tx.NewID("note")
	if err != nil {
		return pack.Result{}, err
	}
	n := Note{Title: in.Title, Body: in.Body, Author: c.Context.Actor.Identity, Tags: in.Tags}
	if n.Tags == nil {
		n.Tags = []string{}
	}
	o := &pack.Object{ID: id, Type: noteType, Status: "draft"}
	if err := save(c, o, n, 0); err != nil {
		return pack.Result{}, err
	}
	if err := c.Tx.Emit("sample.note.created", id, map[string]any{"noteId": id, "author": n.Author}); err != nil {
		return pack.Result{}, err
	}
	return pack.Result{Status: http.StatusCreated, Body: map[string]any{"id": id, "version": o.Version, "status": o.Status}}, nil
}

func (Pack) edit(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	in, err := parse(raw)
	if err != nil {
		return pack.Result{}, err
	}
	o, n, err := load(c, in.Target)
	if err != nil {
		return pack.Result{}, err
	}
	if n.Author != c.Context.Actor.Identity {
		return pack.Result{}, pack.NewProblem(http.StatusForbidden, "SAMPLE_NOT_AUTHOR", "only the author can edit a draft", "")
	}
	if o.Status != "draft" {
		return pack.Result{}, bad("SAMPLE_INVALID_STATE", "only drafts can be edited")
	}
	if in.Title != nil {
		n.Title = in.Title
	}
	if in.Body != "" {
		n.Body = in.Body
	}
	if err := save(c, o, n, o.Version); err != nil {
		return pack.Result{}, err
	}
	return pack.Result{Status: http.StatusOK, Body: map[string]any{"id": o.ID, "version": o.Version}}, nil
}

func transition(c *pack.CommandCtx, raw json.RawMessage, from, to, event string, needRole string) (pack.Result, error) {
	in, err := parse(raw)
	if err != nil {
		return pack.Result{}, err
	}
	if needRole != "" && !slices.Contains(c.Context.Roles, needRole) {
		return pack.Result{}, pack.NewProblem(http.StatusForbidden, "SAMPLE_FORBIDDEN", "the "+needRole+" role is required", "")
	}
	o, n, err := load(c, in.Target)
	if err != nil {
		return pack.Result{}, err
	}
	if o.Status != from {
		return pack.Result{}, bad("SAMPLE_INVALID_STATE", "note is "+o.Status+", expected "+from)
	}
	if to == "published" {
		n.PublishedAt = c.Temporal.Now()
	}
	o.Status = to
	if err := save(c, o, n, o.Version); err != nil {
		return pack.Result{}, err
	}
	if err := c.Tx.Emit(event, o.ID, map[string]any{"noteId": o.ID}); err != nil {
		return pack.Result{}, err
	}
	return pack.Result{Status: http.StatusOK, Body: map[string]any{"id": o.ID, "version": o.Version, "status": o.Status}}, nil
}

func (Pack) publish(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	return transition(c, raw, "draft", "published", "sample.note.published", "sample-editor")
}

func (Pack) archive(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	return transition(c, raw, "published", "archived", "sample.note.archived", "sample-editor")
}

func (Pack) schedule(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	in, err := parse(raw)
	if err != nil {
		return pack.Result{}, err
	}
	o, n, err := load(c, in.Target)
	if err != nil {
		return pack.Result{}, err
	}
	trig, err := c.Temporal.Schedule("remind:"+o.ID+":"+in.At, in.At, "sample:RemindNote", o.ID, nil)
	if err != nil {
		return pack.Result{}, err
	}
	n.RemindAt = in.At
	if err := save(c, o, n, o.Version); err != nil {
		return pack.Result{}, err
	}
	return pack.Result{Status: http.StatusOK, Body: map[string]any{"id": o.ID, "trigger": trig}}, nil
}

func view(o *pack.Object) map[string]any {
	var n Note
	_ = json.Unmarshal(o.Attributes, &n)
	return map[string]any{"id": o.ID, "type": o.Type, "version": o.Version, "status": o.Status, "attributes": n}
}

func (Pack) get(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	in, err := parse(raw)
	if err != nil {
		return pack.Result{}, err
	}
	o, err := c.Tx.Get(noteType, in.Target)
	if err != nil {
		return pack.Result{}, err
	}
	return pack.Result{Status: http.StatusOK, Body: view(o)}, nil
}

func (Pack) list(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	var in struct {
		Size   int    `json:"size"`
		Cursor string `json:"cursor"`
	}
	_ = json.Unmarshal(raw, &in)
	objs, err := c.Tx.List(noteType, in.Size, in.Cursor)
	if err != nil {
		return pack.Result{}, err
	}
	items := make([]any, 0, len(objs))
	for _, o := range objs {
		items = append(items, view(o))
	}
	page := map[string]any{"hasMore": in.Size > 0 && len(objs) == in.Size}
	if len(objs) > 0 {
		page["nextCursor"] = objs[len(objs)-1].ID
	}
	return pack.Result{Status: http.StatusOK, Body: map[string]any{"items": items, "page": page}}, nil
}

// remind is fired by the trigger engine (system actor) and refused for anyone else.
func (Pack) remind(c *pack.CommandCtx, raw json.RawMessage) (pack.Result, error) {
	if c.Context.Actor.Kind != "service" {
		return pack.Result{}, pack.NewProblem(http.StatusForbidden, "SAMPLE_FORBIDDEN", "reminders are fired by the trigger engine only", "")
	}
	in, err := parse(raw)
	if err != nil {
		return pack.Result{}, err
	}
	o, _, err := load(c, in.Target)
	if err != nil {
		return pack.Result{}, err
	}
	if err := c.Tx.Emit("sample.note.reminded", o.ID, map[string]any{"noteId": o.ID}); err != nil {
		return pack.Result{}, err
	}
	return pack.Result{Status: http.StatusOK, Body: map[string]any{"id": o.ID}}, nil
}
