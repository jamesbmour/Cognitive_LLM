from ai_bricks.api import openai
import stats
import os

# from openai import OpenAI

openai.api_key = os.getenv('OPENAI_API_KEY')

DEFAULT_USER = os.getenv('COMMUNITY_USER', '')


# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def use_key(key):
    openai.use_key(key)


usage_stats = stats.get_stats(user=DEFAULT_USER)


def set_user(user):
    global usage_stats
    usage_stats = stats.get_stats(user=user)
    openai.set_global('user', user)
    openai.add_callback('after', stats_callback)


def complete(text, **kw):
    model = kw.get('model', 'gpt-3.5-turbo')
    llm = openai.model(model)
    llm.config['pre_prompt'] = 'output only in raw text'  # for chat models
    resp = llm.complete(text, **kw)
    resp['model'] = model
    return resp


def embedding(text, **kw):
    model = kw.get('model', 'text-embedding-ada-002')
    llm = openai.model(model)
    resp = llm.embed(text, **kw)
    resp['model'] = model
    return resp


def embeddings(texts, **kw):
    model = kw.get('model', 'text-embedding-ada-002')
    llm = openai.model(model)
    resp = llm.embed_many(texts, **kw)
    resp['model'] = model
    return resp


tokenizer_model = openai.model('text-davinci-003')


def get_token_count(text):
    return tokenizer_model.token_count(text)


def stats_callback(out, resp, self):
    model = self.config['model']
    usage = resp['usage']
    usage['call_cnt'] = 1
    if 'text' in out:
        usage['completion_chars'] = len(out['text'])
    elif 'texts' in out:
        usage['completion_chars'] = sum([len(text) for text in out['texts']])
    # TODO: prompt_chars
    # TODO: total_chars
    if 'rtt' in out:
        usage['rtt'] = out['rtt']
        usage['rtt_cnt'] = 1
    usage_stats.incr(f'usage:v4:[date]:[user]', {f'{k}:{model}': v for k, v in usage.items()})
    usage_stats.incr(f'hourly:v4:[date]', {f'{k}:{model}:[hour]': v for k, v in usage.items()})


# print('STATS_CALLBACK', usage, flush=True) # XXX

def get_community_usage_cost():
    data = usage_stats.get(f'usage:v4:[date]:{DEFAULT_USER}')
    used = 0.0
    used += 0.04 * data.get('total_tokens:gpt-4', 0) / 1000  # prompt_price=0.03 but output_price=0.06
    used += 0.02 * data.get('total_tokens:text-davinci-003', 0) / 1000
    used += 0.002 * data.get('total_tokens:text-curie-001', 0) / 1000
    used += 0.002 * data.get('total_tokens:gpt-3.5-turbo', 0) / 1000
    used += 0.0004 * data.get('total_tokens:text-embedding-ada-002', 0) / 1000
    return used


if __name__ == '__main__':
    # load .env file
    from dotenv import load_dotenv

    load_dotenv()

    print(complete('Once upon a time,'))
    print(embedding('Once upon a time,'))
    print(embeddings(['Once upon a time,', 'In a galaxy far, far away.']))
    print(get_token_count('Once upon a time,'))
