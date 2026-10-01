# RL Monitoring Grounded Theory and Architectural Design Decisions

This project provides Grounded Theory coding, CodeableModels ADDs models, and PlantUML model view generation for the RL Monitoring ADDs paper.

## Contents
`_generated` - The generated UML model views.

`memos` - The Grounded Theory memos for ADDs, decision options, decision drivers and sources.

`src/generators` - Script(s) for generating model views.

`src/metamodels` - Grounded Theory and CodeableModels metamodel extensions.

`src/model` - The CodeableModels ADD model instance.

`LICENSE` - The software license for the repository.

`README.md` - This file.

### Prerequisites / Installing

The project was developed with Python 3.12.

The [PlantUML](http://plantuml.com/download) jar file and  
[CodeableModels](https://github.com/uzdun/CodeableModels/) 
are required and the PYTHONPATH must be correctly set:

* The directory containing `codeableModels` and `plantUMLRenderer` must be on the PYTHONPATH.
* The directory containing this project must be on the PYTHONPATH.

See plantUMLRenderer directory in [Codeable Models](https://github.com/uzdun/CodeableModels/) for instructions how
to set up the plant UML jar.

Without further configuration, it is assumed to be in the default directory:

```
self.plant_uml_jar_path = "../../../libs/plantuml.jar"
```

Without further configuration, model views are assumed to be generated in:
```
self.directory = "../../_generated"
```

### Generating the models:

Assuming the following:
- This project is located in `/home/user/dev/add/rlmonitoringadds`.
- `CodeableModels` is located in `/home/user/dev/add/CodeableModels`.
- `plant_uml.jar` is located in `/home/user/dev/add/libs`.
- The values of neither `self.directory` nor `self.plant_uml_jar_path` have been changed.

Then the models can be generated as follows:

```
export PYTHONPATH="/home/user/dev/add/CodeableModels:/home/user/dev/add/rlmonitoringadds"

python /home/user/dev/add/rlmonitoringadds/src/generators/generate_views.py
```
## Built With

* [Codeable Models](https://github.com/uzdun/CodeableModels/) - Modelling framework
* [PlantUML](http://plantuml.com/download) - Model view generation


## Authors

Zhizhou Fang, Stephen John Warnett, Uwe Zdun

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE)
file for details