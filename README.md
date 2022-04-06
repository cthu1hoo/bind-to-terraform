# Imports BIND9 zone files to Terraform (hashicorp/dns)

Generates both configuration snippets and import commands. For now, only supports A, CNAME, and TXT records.

## Usage:

### Generate Terraform configuration file:

```sh
./bind_to_terraform.py db.example example.com | tee zones.tf
```

### Import existing resources into state file:

```
grep '# import' zones.tf | sed 's/# //' | sh -
```

Adjust as necessary.