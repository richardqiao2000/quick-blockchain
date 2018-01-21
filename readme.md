## A quick block chain and coin mining implementation
### install python3.6 and Flask
```bash
pip install Flask==0.12.2 requests==2.18.4
```
### run it at local
```bash
# 1. start 2 block chain nodes
python3 blockchain.py 5000
python3 blockchain.py 5001

# 2. register each other
curl -X POST -H "Content-Type: application/json" -d '{
  "nodes": ["http://0.0.0.0:5001"]
}' "http://localhost:5000/nodes/register"

curl -X POST -H "Content-Type: application/json" -d '{
  "nodes": ["http://0.0.0.0:5000"]
}' "http://localhost:5001/nodes/register"


# 3. Mine and display it on 0.0.0.0:5000
curl -X GET -H "Content-Type: application/json" "http://localhost:5000/mine"
curl -X GET -H "Content-Type: application/json" "http://localhost:5000/chain"

# 4. Display then Resolve it on 0.0.0.0:5001
curl -X GET -H "Content-Type: application/json" "http://localhost:5001/chain"
curl -X GET -H "Content-Type: application/json" "http://localhost:5001/nodes/resolve"
curl -X GET -H "Content-Type: application/json" "http://localhost:5001/chain"

# 5. Add transaction on 0.0.0.0:5001
curl -X POST -H "Content-Type: application/json" -d '{
 "sender": "bill gates",
 "recipient": "ma yun",
 "amount": 5
}' "http://localhost:5001/transaction/new"


# 6. Mine it on 0.0.0.0:5001
curl -X GET -H "Content-Type: application/json" "http://localhost:5001/mine"
curl -X GET -H "Content-Type: application/json" "http://localhost:5001/chain"

# 7. Resolve it on 0.0.0.0:5000
curl -X GET -H "Content-Type: application/json" "http://localhost:5000/chain"
curl -X GET -H "Content-Type: application/json" "http://localhost:5000/nodes/resolve"
curl -X GET -H "Content-Type: application/json" "http://localhost:5000/chain"

# 8. display blocks on both. They should display same chain
curl -X GET -H "Content-Type: application/json" "http://localhost:5000/chain"
curl -X GET -H "Content-Type: application/json" "http://localhost:5001/chain"

```