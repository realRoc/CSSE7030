def read_config(filename):
    """Returns a dictionary representation of the configuration data.

    Configuration data is in sections, indicated by [Section Name].
    Within each section is a set of key to value maps as key=value.

    Parameters:
        filename (str): Name of the configuration file from which to extract data.

    Return:
        dict<str: dict<str: str>>: Sections are keys for dictionaries containing the section's entries.
                                   Each key-value pair within a section is a dictionary entry.
    """

    fd = open(filename, 'r')

    # Resulting configuration dictionary
    config = {}

    # Store the current heading (i.e. the last one encountered)
    heading = None

    # Iterate over each line in the file.
    for line in fd:
        # First strip the line of surrounding whitespace.
        line = line.strip()

        if line.startswith('==') and line.endswith('=='):
            # If the line is wrapped with square brackets, it is a major key.

            # The heading does not include [ or ]
            heading = line[2:-2]

            # Create a new dictionary for the settings under this heading.
            config[heading] = {}

        elif line.count(':') == 1 and heading is not None:
            # Else if this line contains equals and we've seen a heading.

            # Get the name and value from this line.
            name, value = line.split(' : ')

            # Set the appropriate key/value in the configuration dictionary
            # for the current heading.
            config[heading][name.strip()] = value.strip()

        #else:
            # If the config file is invalid, raise a ValueError.
            #raise ValueError('Invalid config file.')

    fd.close()

    return config


def get_value(config, name):
    """Returns the setting name from the configuration dictionary.

    Parameters:
        config (dict<str: dict<str: str>>): Section to Setting-Value mapping.
        name (str): Name of the setting we want to identify.

    Return:
        (str): Value of 'name's setting.
    """
    # Split the name of the setting over the fullstop.
    a, b = name.split('.')

    # Return the appropriate value.
    return config[a][b]



    #config = read_config('config.txt')
    #print(get_value(config, 'user.mobile'))
    #print(get_value(config, 'notifications.email'))
