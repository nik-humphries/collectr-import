# We are going to test hitting the API and see if it works, see what headers etc. we need
# We need to construct a post request and add an auth header

# Auth token is in config.yaml and needs to be read in 

def get_token():
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config['default']['auth']['token']