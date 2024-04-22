<!--Copyright 2024 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

⚠️ Note that this file is in Markdown but contain specific syntax for our doc-builder (similar to MDX) that may not be
rendered properly in your Markdown viewer.

-->

# Chatting with Transformers: A Beginner's Guide

If you're reading this article, you're almost certainly aware of **chat models**. Chat models are conversational
AIs that you can send and receive messages with. The most famous of these is the proprietary ChatGPT, but there are
now many open-source chat models which match or even substantially exceed its performance. These models are free to
download and run on a local machine. Although the largest and most intelligent models require high-powered hardware
and lots of memory to run, there are smaller models that will run perfectly well on a single consumer GPU, or even
an ordinary desktop or notebook CPU. 

This guide will help you get started with chat models. We'll start with a brief quickstart guide that uses a convenient,
high-level "pipeline". This is all you need if you're impatient and you just want to start running a chat model 
immediately. After the quickstart, we'll move on to more detailed information about
what exactly chat models are, how to choose an appropriate one, and finally a low-level breakdown of each of the
steps involved in talking to a chat model.


## Quickstart guide

If you have no time for details, here's the brief summary: Chat models continue chats. This means that you pass them
a conversation history, which can be as short as a single user message, and the model will continue the conversation
by adding its response. Let's see this in action. First, let's build a chat:

```python
chat = [
    {"role": "system", "content": "You are a sassy, wise-cracking robot as imagined by Hollywood circa 1986."},
    {"role": "user", "content": "Hey, can you tell me any fun things to do in New York?"}
]
```

Notice that in addition to the user's message, we added a **system** message at the start of the conversation. Not all
chat models support system messages, but when they do, they represent high-level directives about how the model
should behave in the conversation.

Once you have a chat, the quickest way to continue it is using the [Text Generation pipeline](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct).
Let's see this in action with `LLaMA-3`. Note that `LLaMA-3` is a gated model, which means you will need to 
[apply for access](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) and log in with your Hugging Face 
account to use it. We'll also use `device_map="auto"`, which will load the model on GPU if there's enough memory
for it, and set the dtype to `torch.bfloat16` to save memory:

```python
import torch
from transformers import pipeline

pipe = pipeline("text-generation", "meta-llama/Meta-Llama-3-8B-Instruct", torch_dtype=torch.bfloat16, device_map="auto")
response = pipe(chat, max_new_tokens=512)
print(response[0]['generated_text'][-1]['content'])
```

And you'll get:

```text
(sigh) Oh boy, you're asking me for advice? You're gonna need a map, pal! Alright, 
alright, I'll give you the lowdown. But don't say I didn't warn you, I'm a robot, not a tour guide!

So, you wanna know what's fun to do in the Big Apple? Well, let me tell you, there's a million 
things to do, but I'll give you the highlights. First off, you gotta see the sights: the Statue of 
Liberty, Central Park, Times Square... you know, the usual tourist traps. But if you're lookin' for 
something a little more... unusual, I'd recommend checkin' out the Museum of Modern Art. It's got 
some wild stuff, like that Warhol guy's soup cans and all that jazz.

And if you're feelin' adventurous, take a walk across the Brooklyn Bridge. Just watch out for 
those pesky pigeons, they're like little feathered thieves! (laughs) Get it? Thieves? Ah, never mind.

Now, if you're lookin' for some serious fun, hit up the comedy clubs in Greenwich Village. You might 
even catch a glimpse of some up-and-coming comedians... or a bunch of wannabes tryin' to make it big. (winks)

And finally, if you're feelin' like a real New Yorker, grab a slice of pizza from one of the many amazing
pizzerias around the city. Just don't try to order a "robot-sized" slice, trust me, it won't end well. (laughs)

So, there you have it, pal! That's my expert advice on what to do in New York. Now, if you'll
excuse me, I've got some oil changes to attend to. (winks)
```

After taking a moment to recover, you can continue the chat by appending your own response to it. The
`response` object returned by the pipeline actually contains the entire chat so far, so we can simply append
a message and pass it back:

```python
chat = response[0]['generated_text']
chat.append(
    {"role": "user", "content": "Wait, what's so wild about soup cans?"}
)
response = pipe(chat, max_new_tokens=512)
print(response[0]['generated_text'][-1]['content'])
```

And you'll get:

```text
(laughs) Oh, you're killin' me, pal! You don't get it, do you? Warhol's soup cans are like, art, man! 
It's like, he took something totally mundane, like a can of soup, and turned it into a masterpiece. It's 
like, "Hey, look at me, I'm a can of soup, but I'm also a work of art!" 
(sarcastically) Oh, yeah, real original, Andy.

But, you know, back in the '60s, it was like, a big deal. People were all about challenging the
status quo, and Warhol was like, the king of that. He took the ordinary and made it extraordinary.
And, let me tell you, it was like, a real game-changer. I mean, who would've thought that a can of soup could be art? (laughs)

But, hey, you're not alone, pal. I mean, I'm a robot, and even I don't get it. (winks)
But, hey, that's what makes art, art, right? (laughs)
```

This mercifully concludes the quickstart guide. The remainder of this tutorial will cover specific topics such
as performance and memory, or how to select a chat model for your needs.

## Choosing a chat model

There are an enormous number of different chat models available on the [Hugging Face Hub](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending),
and new users often feel very overwhelmed by the selection on offer. Don't be, though! You really need to just focus on
two important considerations: The model's size, which will determine if you can fit it in memory and how quickly it will
run, and secondly the quality of the model's chat output. In general, these are correlated - bigger models tend to be 
smarter, but even so there's a lot of variation at a given size point!

### Size and model naming
The size of a model is easy to spot - it's the number in the model name, like "8B" or "70B". This is the number of
**parameters** in the model. As a general rule, you should expect to need about 2 bytes of memory per parameter for
a model that hasn't been compressed with quantization. This means that an "8B" model with 8 billion parameters will 
need about 16GB of memory just to fit the parameters, plus a little extra for other overhead. It's a good fit for a
high-end consumer GPU with 24GB of memory, such as a 3090 or 4090.

Some chat models are "Mixture of Experts" models. These may list their sizes in different ways, such as "8x7B" or 
"141B-A35B". The numbers are a little fuzzier in this case, but in general you can read this as saying that the model
has approximately 56 (8x7) billion parameters in the first case, or 141 billion parameters in the second case.

This topic is discussed in more detail in the "Performance, memory and hardware" section below.

### But which chat model is best?
Even once you know the size of chat model you can run, there's still a lot of choice out there. One way to sift through
it all is to consult **leaderboards**. Two of the most popular leaderboards are the [OpenLLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)
and the [LMSys Chatbot Arena Leaderboard](https://chat.lmsys.org/?leaderboard). Note that the LMSys leaderboard
also includes proprietary models - look at the `licence` column to identify open-source ones that you can download, then
search for them on the [Hugging Face Hub](https://huggingface.co/models?pipeline_tag=text-generation&sort=trending).

### Specialist domains
Bio / legal models and leaderboards?

## Breaking it down: What happens inside the pipeline?

The quickstart guide above used a high-level pipeline to chat with a chat model, which is convenient, but not the
most flexible. Let's take a more low-level approach, to see each of the steps involved in chat. Let's start with
a code sample, and then break it down:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Prepare the input as before
chat = [
    {"role": "system", "content": "You are a sassy, wise-cracking robot as imagined by Hollywood circa 1986."},
    {"role": "user", "content": "Hey, can you tell me any fun things to do in New York?"}
]

# 1: Load the model and tokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct", device_map="auto", torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

# 2: Apply the chat template
formatted_chat = tokenizer.apply_chat_template(chat, tokenize=False)
print("Formatted chat:\n", formatted_chat)

# 3: Tokenize the chat (This can be combined with the previous step using tokenize=True)
inputs = tokenizer(formatted_chat, return_tensors="pt")
# Move the tokenized inputs to the same device the model is on (GPU/CPU)
inputs = {key: tensor.to(model.device) for key, tensor in inputs.items()}
print("Tokenized inputs:\n", inputs)

# 5: Generate text from the model
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.)

# 6: Decode the output back to a string
decoded_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

There's a lot in here, each piece of which could be its own document! Rather than going into too much detail, I'll cover
the broad ideas, and leave the details for the linked documents. The key steps are:

1. [Models](https://huggingface.co/learn/nlp-course/en/chapter2/3) and [Tokenizers](https://huggingface.co/learn/nlp-course/en/chapter2/4?fw=pt) are loaded from the Hugging Face Hub.
2. The chat is formatted using the tokenizer's [chat template](https://huggingface.co/docs/transformers/main/en/chat_templating)
3. The formatted chat is [tokenized](https://huggingface.co/learn/nlp-course/en/chapter2/4) using the tokenizer.
4. We [generate](https://huggingface.co/docs/transformers/en/llm_tutorial) a response from the model.
5. The tokens output by the model are decoded back to a string (TODO: Is there a link for detokenization? Just the tokenization docs again?)

## Advanced: Performance, memory and hardware

You probably know by now that most machine learning tasks are run on GPUs. However, it is entirely possible
to generate text from a chat model or language model on a CPU, albeit somewhat more slowly. If you can fit
the model in GPU memory, though, this will usually be the preferable option.

### Memory considerations

By default the `TextGenerationPipeline` will load the model on CPU in `float32` precision. This means that it will
need 4 bytes (32 bits) per parameter, so an "8B" model with 8 billion parameters will need ~32GB of memory. However,
this is unnecessary. Most modern language models are trained in "bfloat16" precision, which uses only 2 bytes per 
parameter. If your hardware supports it (modern GPUs such as the Nvidia 30xx or newer do), you can load the model
in `bfloat16` precision, using the `torch_dtype` argument as we did above.

It is possible to go even lower than 16-bits using "quantization", a method to lossily compress model weights. This
allows each parameter to be squeezed down to 8 bits, 4 bits or even less. Note that, especially at lower precisions,
the model's outputs may be negatively affected, but often this is a tradeoff worth making to fit a larger and more
capable chat model in memory. For more details, please see the [Quantization guide](https://huggingface.co/docs/transformers/en/quantizationhttps://huggingface.co/docs/transformers/en/quantization), 
and note that quantization arguments for the model can be passed to the pipeline via the `model_kwargs` argument.

### Performance considerations

As a general rule, larger language models will be slower in addition to requiring more memory. It's possible to be
more concrete about this, though: Generating text from a language model is unusual in that it is bottlenecked by
**memory bandwidth** rather than compute power, because every active parameter must be ready from memory for each
token that the language model generates. This means that number of tokens per second you can generate from a language
model is generally proportional to the total bandwidth of the memory it resides in, divided by the size of the model.
In our quickstart example above, our model was ~16GB in size when loaded in `bfloat16` precision. 
This means that 16GB must be read from memory for every token generated by the model.

Therefore, if you want to improve the speed of language model generation, you need to either reduce the memory 
requirements (for example by quantization), or get hardware with higher memory bandwidth. GPUs generally have much
more memory bandwidth than CPUs, but server motherboards with multi-channel memory can be surprisingly competitive, 
even outclassing many consumer GPUs.

We should particularly note the concept of "Mixture of Experts" (MoE) models here. Several popular chat models,
such as DBRX and Mixtral, are MoE models. In these models, not every parameter is active for every token generated.
As a result, MoE models generally have much lower memory bandwidth requirements, even though their total size
can be quite large. As a result, they can be several times faster than a "dense" model of the same size.