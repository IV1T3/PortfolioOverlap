import json

def load_json_data(type):
        try:
            with open("portfoliooverlap/data/"+ type +".json", "r") as f:
                mapping = json.load(f)
        except FileNotFoundError:
            mapping = {}
        except json.decoder.JSONDecodeError:
            mapping = {}
        
        return mapping
    
def write_json_data(type, json_data, save_human_readable=True):
    with open("portfoliooverlap/data/"+ type +".json", "w") as f:
        if save_human_readable:
            json.dump(json_data, f, indent=4, sort_keys=True)
        else:
            json.dump(json_data, f, sort_keys=True)
        