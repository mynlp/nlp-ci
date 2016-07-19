## Job list for registering to Jenkins

```json
[
  {
    ".title":"jigg",
    ".contents":{
      "base-project": {
        "repository":"https://github.com/mynlp/jigg-test.git",
        "branch":"master"
      },
      "test-projects":[
        {
          "repository":"https://github.com/mynlp/jigg.git",
          "branch":"develop"
        }
      ]
    }
  }
]
```

- `.title`: Job name.
- `.contents`: Contents of base and test projects.
  - `base-project`: A description of base project.
  - `test-projects`: Array of test-project description.
