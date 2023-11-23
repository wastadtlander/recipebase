# Connecting with Config

To connect, create a config.py file in the root of the director containing the following:

```python
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ENTER YOUR PASSWORD HERE',
    'database': 'recipebase'
}
```

Then run connection.py
For me, it's done via `python3 connection.py`

# Build database

To rebuild the database after changes have been made to it, run the following:

1. On the command line, run `mysql -u root -p`
2. Enter `show databases;`
3. `DROP DATABASE recipebase;` Your database may be called something else
4. `CREATE DATABASE recipebase;`
5. `USE recipebase;`
6. `SOURCE recipe_base_database.sql`
7. `quit`
