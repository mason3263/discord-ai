from openai import OpenAI
import asyncio

class GPT:

    def __init__(self, api_key: str, assistant_id: str):
        self.client = OpenAI(api_key=api_key)

        self.assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistant_id
        )

        self.thread = self.client.beta.threads.create()
        
    async def run(self, message_id) -> str:
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions="Please address the user as Discord User. The user has a premium account."
        )

        while run.status in ['queued', 'in_progress', 'cancelling']:
            await asyncio.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )

        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id
            )

        message = ""
        for content in messages.data[0].content:
            message += content.text.value

        return message
    
    async def add_message(self, message: str) -> str:
        gpt_message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

        return await self.run(gpt_message.id)
    
    def clear(self):
        self.client.beta.threads.delete(
            thread_id=self.thread.id
        )

        self.thread = self.client.beta.threads.create()