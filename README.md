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
# Edit secrets.yml to add your API key etc.
cp secrets.example.yml secrets.yml

# Invoke locally
serverless invoke local -f trade

# Deploy to AWS Lambda
serverless deploy
```
