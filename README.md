Bargain is a Serverless cryptocurrency trading bot
==================================================

> I'd buy that for a dollar!

![I'd buy that for a dollar!](id-buy-that-for-a-dollar.jpg)


Local setup
-----------

[Installing Python 3 on Mac OS X](http://python-guide-pt-br.readthedocs.io/en/latest/starting/install3/osx/ )

```
#!bash
# Install development version
pip3 install -e .

# Invoke locally
bargain
```


Serverless setup
----------------

[Serverless AWS Quick Start](https://serverless.com/framework/docs/providers/aws/guide/quick-start/)

```
#!bash
# Edit secrets.yml to set your API key and secret
cp config/secrets.example.yml config/secrets.yml

# Edit trades.yml to configure your trades
cp config/trades.example.yml config/trades.yml

# Invoke locally
serverless invoke local -f trade

# Deploy to AWS Lambda
serverless deploy
```
