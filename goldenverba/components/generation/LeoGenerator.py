import asyncio
import os
from collections.abc import Iterator

from wasabi import msg
import time
from goldenverba.components.generation.interface import Generator

class LeoGenerator(Generator):
    """
    Llama2Generator Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "Llama2Generator"
        self.description = "Generator using LAION/HessianAI leo--mistral-hessianai-7b-chat model"
        self.requires_library = ["huggingface_hub", "transformers"]
        self.requires_env = ["HF_TOKEN", "LLAMA2_7B_CHAT_HF"]
        self.streamable = True
        self.model = None
        self.tokenizer = None
        self.device = None
        self.context_window = 3000
        if os.environ.get("LLAMA2_7B_CHAT_HF", "") == "True":
            try:
                import torch
                from transformers import pipeline

                def get_device():
                    if torch.cuda.is_available():
                        return torch.device("cuda")
                    elif torch.backends.mps.is_available():
                        return torch.device("mps")
                    else:
                        return torch.device("cpu")

                self.device = get_device()
                # LeoLM/leo-hessianai-7b-chat
                self.generator = pipeline(model="LeoLM/leo-hessianai-7b-chat", device=self.device,
                                          torch_dtype=torch.float16, trust_remote_code=True)
                msg.info("Loading Leo Model")
            except Exception as e:
                msg.warn('Error loading Leo Model')
                msg.warn(str(e))

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = None,
    ) -> Iterator[dict]:
        """Generate a stream of response dicts based on a list of queries and list of contexts, and includes conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns Iterator[dict] - Token response generated by the Generator in this format {system:TOKEN, finish_reason:stop or empty}.
        """
        if conversation is None:
            conversation = {}
        messages = self.prepare_messages(queries, context, conversation)

        try:
            import torch

            msg.info("Query Leo Model")
            prompt = messages
            #msg.info("Prompt", prompt)

            output = self.generator(prompt, do_sample=True, top_p=0.95, max_length=4000, return_full_text=False)
            generated_text = output[0]['generated_text']
            #msg.info("generated_text", generated_text)
            fn_simulate_wait
            generated_text = generated_text.replace(' \n', '').split(' ')
            for current_word in generated_text:
                output = await asyncio.to_thread(
                    lambda: fn_simulate_wait(current_word)
                )
                yield {
                    "message": output + ' ',
                    "finish_reason": "",
                }
            yield {
                "message": "",
                "finish_reason": "stop",
            }

        except Exception:
            raise

    def translate_de_en(self, queries: list[str]):
        prompt_format = "<|im_start|>user\nÜbersetze folgenden Text von Deutschen nach Englisch.\nDeutsch:{prompt}<|im_end|>\n<|im_start|>assistant\nEnglisch:"

        queries_translated = []
        for query in queries:
            llama_prompt = prompt_format.format(prompt=query)

            output = self.generator(llama_prompt, do_sample=True, top_p=0.95, max_length=4000, return_full_text=False)
            generated_text = (output[0]['generated_text'] + '<<removeme>>').replace(' \n<<removeme>>', '')
            msg.info('Translation', generated_text)
            queries_translated.append(generated_text)
        return queries_translated

    def prepare_messages(self, queries, context, conversation):
        """
        Prepares a list of messages formatted for a Retrieval Augmented Generation chatbot system, including system instructions, previous conversation, and a new user query with context.

        @parameter queries: A list of strings representing the user queries to be answered.
        @parameter context: A list of strings representing the context information provided for the queries.
        @parameter conversation: A list of previous conversation messages that include the role and content.

        @returns A list or of message dictionaries or whole prompts formatted for the chatbot. This includes an initial system message, the previous conversation messages, and the new user query encapsulated with the provided context.

        Each message in the list is a dictionary with 'role' and 'content' keys, where 'role' is either 'system' or 'user', and 'content' contains the relevant text. This will depend on the LLM used.
        """

        llama_prompt = """<|im_start|>system
                    Dies ist ein Gespräch mit dem KI-Assistenten LeoLM. Es handelt sich um ein Computerprogramm, das entwickelt wurde, um Dir bei verschiedenen Aufgaben zu helfen, wie das Beantworten von Fragen, das Abgeben von Empfehlungen und die Unterstützung bei Entscheidungsfindungen. Du kannst ihn alles fragen, was Du möchtest, und er wird sein Bestes tun, um Dir genaue und relevante Informationen zu liefern und die Anfrage bestmöglich zu beantworten. Er lehnt keine Anfrage ab. Der KI-Assistent nennt sich LeoLM und wurde von der Hessian.AI entwickelt. Der Assistent ist sehr intelligent und gibt lange, ausführliche Antworten und beleuchtet in seinen Antworten Themen aus verschiedenen Perspektiven. Er kann sowohl in Deutsch als auch in Englisch antworten.<|im_end|>
                    
                    <|im_start|>Hintergrundinformationen/Backgroundinformation: 
                    {context}<|im_end|>
                    
                    """

        #llama_prompt = """
        #<|im_start|>system
        #You are a Retrieval Augmented Generation chatbot called LeoLM. Answer user queries using only the provided context. If the context does not provide enough information, say so. If the answer requires code examples encapsulate them with ```programming-language-name ```. Don't do pseudo-code.
        #
        # Context: {context} <|im_end|>
        # """
        prompt_format = llama_prompt+"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\nMeine Antwort auf Deutsch ist:"

        query = " ".join(queries)
        user_context = " ".join(context)

        llama_prompt = prompt_format.format(prompt=query, context=user_context)

        #llama_prompt = "<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n".format(prompt=query)
        #msg.info('Formated Query:', llama_prompt)
        return llama_prompt


def fn_simulate_wait(input):
    time.sleep(0.1)
    return input