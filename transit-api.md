You have until 20 mins,

Skip the threat check please as we dont have as much time as we wanted

Your goal is not to expose raw GTFS feeds directly. Your goal is to design and ship a developer-friendly API on top of a messy real-world dataset.

Use the provided local GTFS files as your source of truth. Work from local files only. Do not rely on live API calls.

Dataset zip: https://storage.googleapis.com/interview-assignment-vibe-the-tube/vibe-the-tube-candidate-bundle.zip

You may use any language, framework, tools, and architecture you want.

AI tooling is required. Use whatever coding assistants or agents you prefer.

There is more data here than you can reasonably model in this timeframe. Your job is to decide what slice of the problem is worth solving, what complexity to hide, and what API surface would actually be useful to another developer.

IMPORTANT: Don’t break apart the task just to show us you understand. The end result is what matters

- This is all swedens transport data

These are the goals we want to achieve: 
- query by geography - returned available options by city
- time tables by route, time to next arival, starting at route -> where can you end? , query by terminus (ie starting in location A, I want to go to location B return my options or "Sorry there are no options available")
- query by type of transport ie train | metro | bus | boat