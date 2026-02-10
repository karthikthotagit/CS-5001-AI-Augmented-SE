# Classroom CLI Agent (cca) - Ollama-only

Default model: devstral-small-2:24b-cloud
Override:
- --model <name>
- OLLAMA_MODEL environment variable

## Install
pip install -e .

## Start Ollama and pull model
ollama serve
ollama pull devstral-small-2:24b-cloud

## Create a program
```
cca  --repo demo_repo create   --desc "A calculator with add, subtract, multiply, divide functions"   --module src/calculator.py
```

## Generate tests and iterate until target coverage (natural language)
```
cca --repo output/demo_repo test --desc "A calculator with add, subtract, multiply, divide functions"   --module src/calculator.py   --tests tests/test_calculator.py   --coverage "90 percent"
```

## Commit and push
```
cca --repo output/demo_repo commit --message "Agent: add program + tests" --push
```

## End-to-end

Example 1:

```
cca --repo output/demo_repo full --desc "A calculator with add, subtract, multiply, divide functions" --module src/calculator.py --tests tests/test_calculator.py --coverage "at least ninety five percent"
```


Example 2:

```
cca --repo output/demo_repo full --desc "Create Prime Number Checker in Python" --module src/prime_checker.py --tests tests/test_prime_checker.py --coverage "at least 80 percent"
```

Example 3:

```
cca --repo output/demo_flask full --desc "Create a minimal project with FLASK" --module src/flask.py --tests tests/test_flask.py --coverage "at least 80 percent"
```

```
cca --repo output/demo_streamlit full --desc "Create a project with Streamlit that shows a number is prime or not after taking an input" --module src/app.py --tests tests/test_app.py --coverage "at least 80 percent"
```
