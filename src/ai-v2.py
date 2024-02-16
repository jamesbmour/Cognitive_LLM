
# Importing necessary modules
# from ai_bricks.api import openai
import stats
import os
import stats  # Assuming this is a custom module for tracking stats
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'),
api_key=key)  # Assuming this is a custom module for interfacing with OpenAI API

# TODO: Need to convert from ai_bricks to from openai import OpenAI
# TODO: add a get model function to openai for getting available models from openrouter
# Getting the default user from environment variable, with an empty string as default
DEFAULT_USER = os.getenv('COMMUNITY_USER', '')


# Function to set the API key for OpenAI
def use_key(key):


# Initialize usage statistics for the default user
usage_stats = stats.get_stats(user=DEFAULT_USER)
def set_user(user):
    global usage_stats
    # Update the global usage statistics for the new user
    usage_stats = stats.get_stats(user=user)


# Function to set the user and update usage statistics and callbacks
# def set_user(user):
#     global usage_stats
#     usage_stats = stats.get_stats(user=user)  # Update the global usage statistics for the new user
#     openai.set_global('user', user)  # Set the user in the OpenAI global configuration
#     openai.add_callback('after', stats_callback)  # Register a callback for tracking usage after API calls


# Function to complete text using a specified model, defaulting to 'gpt-3.5-turbo'
def complete(text, **kwargs):
    # model = kw.get('model', 'gpt-3.5-turbo')  # Get the model from keyword arguments, default to 'gpt-3.5-turbo'
    # llm = openai.model(model)  # Instantiate the model
    # llm.config['pre_prompt'] = 'output only in raw text'  # Configure the model to output only raw text
    # resp = llm.complete(text, **kw)  # Make the completion request
    # resp['model'] = model  # Add the model used to the response
    # return resp
    model = kwargs.pop('model', 'text-davinci-003')  # Update to 'text-davinci-003' as a default
    response = client.completions.create(engine=model, prompt=text, **kwargs)
    # The OpenAI Python client automatically uses the API key set globally in `openai.api_key`
    return response



# Function to get the embedding of a text using a specified model
def embedding(text, **kwargs):
    # model = kw.get('model', 'text-embedding-ada-002')  # Default model for embedding
    # llm = openai.model(model)
    # resp = llm.embed(text, **kw)
    # resp['model'] = model
    # return resp
    model = kwargs.pop('model', 'text-embedding-ada-002')  # Using a default embedding model
    response = client.embeddings.create(engine=model, input=text, **kwargs)
    return response



# Function to get embeddings for multiple texts
def embeddings(texts, **kwargs):
    # model = kw.get('model', 'text-embedding-ada-002')
    # llm = openai.model(model)
    # resp = llm.embed_many(texts, **kw)
    # resp['model'] = model
    # return resp
    model = kwargs.pop('model', 'text-embedding-ada-002')  # Using a default embedding model
    response = client.embeddings.create(engine=model, input=texts, **kwargs)
    return response

# Initializing a tokenizer model for token count operations
# tokenizer_model = openai.model('text-davinci-003')
def estimate_token_count(text):
    """
    Estimate the number of tokens in a text string based on whitespace.
    This is a simplified approximation and may not perfectly match OpenAI's tokenization.
    """
    # Basic approximation: Split by spaces (rough approximation for English text)
    tokens = text.split()
    return len(tokens)

# Function to get the token count of a text using the tokenizer model
def get_token_count(text):
    return estimate_token_count(text)




# Callback function for tracking usage statistics after API calls
def stats_callback(out, resp, self):
    model = self.config['model']  # Get the model from the API call configuration
    usage = resp['usage']  # Extract usage data from the response
    usage['call_cnt'] = 1  # Track the number of calls
    # Calculate the number of characters in the completion or embeddings
    if 'text' in out:
        usage['completion_chars'] = len(out['text'])
    elif 'texts' in out:
        usage['completion_chars'] = sum([len(text) for text in out['texts']])
    # Additional usage statistics to be tracked (TODO indicates planned functionality)
    if 'rtt' in out:
        usage['rtt'] = out['rtt']  # Round-trip time of the API call
        usage['rtt_cnt'] = 1  # Count of RTT measurements
    # Increment usage stats in the stats tracking system
    usage_stats.incr(f'usage:v4:[date]:[user]', {f'{k}:{model}': v for k, v in usage.items()})
    usage_stats.incr(f'hourly:v4:[date]', {f'{k}:{model}:[hour]': v for k, v in usage.items()})


# Function to calculate the cost of usage for the community user based on token usage
def get_community_usage_cost():
    data = usage_stats.get(f'usage:v4:[date]:{DEFAULT_USER}')
    used = 0.0
    used += 0.04 * data.get('total_tokens:gpt-4', 0) / 1000
    used += 0.02 * data.get('total_tokens:text-davinci-003', 0) / 1000
    used += 0.002 * data.get('total_tokens:text-curie-001', 0) / 1000
    used += 0.002 * data.get('total_tokens:gpt-3.5-turbo', 0) / 1000
    used += 0.0004 * data.get('total_tokens:text-embedding-ada-002', 0) / 1000
    return used
