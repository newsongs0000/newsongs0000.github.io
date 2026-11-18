# Engineering

We will use `work item`s to ask you to work on assignments; `work item`s are markdown files, existing under the `workItems` directory:

- draft: I will ask you to create TODO work item like: "Create TODO: <Description of what needs to be done, pre-requisites, accept criteria, etc.>", you should create a markdown file under `workItems/draft` directory, the file name should be prefixed by timestamp;
- todo: I will ask you to create TODO work item like: "Create TODO: <Description of what needs to be done, pre-requisites, accept criteria, etc.>", you should create a markdown file under `workItems/todo` directory, the file name should be prefixed by timestamp, creation time be included in the file; or ask you to move `draft` item to `todo` like: "Move the oldest draft to todo directory", or "Move the second oldest draft to todo directory";
- wip: I will ask you to pick up work items to work on like: "Work on the oldest TODO", or "Work on the second oldest TODO", etc.; When you start to work on a TODO, move it from the `todo` directory to this `wip` directory, adding start timestamp;
- completed: When you complete a wip work item, move it to the `completed` directory, adding completiom timestamp;
- archived: I will manually move work items here by myself;
- blocked: If you see any work items are temporarily blocked before other work items complete, put them here.
