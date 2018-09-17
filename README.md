 # Fabric Network Generator Tools
:hammer_and_wrench: hyperledger fabric chaincode network config generator tools.
 
 ## Introduction
  
  Helps you quickly generate a fabric network configuration, reducing cumbersome, repetitive configuration processes and reducing configuration errors. Flexible, highly available generation methods that make it easy to extend your template to customize your own network configuration files.
 ## Preparation
 + python3
 + jinja2
 + pyYAML
 
 ## Features
 
 + generator fabric network core `config` file, create `configtx.yaml`
 + generator fabric `channel` & `block` core config file, create `crypto-config.yaml`
 + generator fabric `orderer/peer` service, create `docker-compose-fabric.yaml`
 + generator fabric `zookeeper/kafka` service, create `docker-compose-zookeeper-kafka.yaml`
 + generator fabric `ca` service and `fabric network` config, create `docker-compose-fabric-template.yaml`
 + generator `couchdb` service, create `docker-compose-couchdb.yaml`
 + generator `prom monitor` service network, create `docker-compose-fabric-monitor.yaml`
 + generator `connect fabric network properties` config, create `fabric-chaincode.*.properties`
 + generator fabric `shell script`, create `generate.sh`
 
 ## Getting started
 ```shell
# clone the project
git clone git@github.com:hooj0/fabric-network-generator.git

# go to project directory
cd fabric-network-generator

# generator config
python generator_tools.py
 ```
 
 ## Usage
 configuration `settings.yaml`
 ```yaml
# -----------------------------------------------------------------
# settings: setter output location, orderer & peer Organization
# -----------------------------------------------------------------
settings:

  # Output fabric network config directory Generator Settings
  output: networks

  # OrdererType: kafka | solo
  orderer_type: solo

  # Orderer Organization Generator Settings
  orderers:
    - name: Orderer1
      domain: example.com
      hostnames: [foo, bar]

    - name: Orderer2
      domain: simple.com
      count: 2

  # Peer Organization Generator Settings
  peers:
    - name: Org1
      domain: hoojo.top
      hostnames: [foo, bar]
      user_count: 2
      template_count: 3

    - name: Org2
      domain: hoojo.me
      user_count: 2
      template_count: 2

  zookeeper:
    domain: simple.xyz
    count: 3

  kafka:
    domain: simple.top
    count: 3
```

execute python command generator fabric network files 
 ```sh
# show help man 
python generator_tools.py -h
python generator_tools.py help

# generator fabric network config
python generator_tools.py
# or
python generator_tools.py gen
```
 
 ## Advanced
  ```bash
 # show help man 
 python generator_tools.py -h
 python generator_tools.py help
 
 # generator fabric network config
 python generator_tools.py gen
 
 # clean fabric network
 python generator_tools.py clean
 
 # add options generator fabric network configs
 python generator_tools.py -c gen
 python generator_tools.py -cx gen
 
 # clean networks
 python generator_tools.py -cx clean gen
 
 # more options
 python generator_tools.py -hcxsfztdmp gen
 python generator_tools.py -hcxsfztdmp clean gen
 ```
 ## Changelog
 
 ## License
[MIT](LICENSE) 
Copyright (c) 2018-hoojo