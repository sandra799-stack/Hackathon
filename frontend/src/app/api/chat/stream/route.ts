import { NextRequest } from "next/server";

const responses = [
  "Hello! How can I help you today?",
  "That's an interesting question. Let me think about that...",
  "I understand your concern. Here's what I think:",
  "Based on what you've told me, I'd suggest:",
  "That's a great point! Have you considered:",
  "I see what you mean. Another way to look at it is:",
  "Thank you for sharing that with me.",
  "Is there anything else I can help you with?",
];

function getRandomResponse(): string {
  return responses[Math.floor(Math.random() * responses.length)];
}

function simulateTyping(
  text: string,
  onChunk: (chunk: string) => void,
  onComplete: () => void
) {
  let index = 0;
  const words = text.split(" ");

  const typeWord = () => {
    if (index < words.length) {
      const word = words[index] + (index < words.length - 1 ? " " : "");
      onChunk(word);
      index++;
      setTimeout(typeWord, Math.random() * 200 + 100);
    } else {
      onComplete();
    }
  };

  setTimeout(typeWord, 500);
}

export async function POST(request: NextRequest) {
  const { message } = await request.json();

  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(
        `data: ${JSON.stringify({ type: "start", content: "" })}\n\n`
      );

      const botResponse = getRandomResponse();
      let accumulatedText = "";

      simulateTyping(
        botResponse,
        (chunk) => {
          accumulatedText += chunk;
          controller.enqueue(
            `data: ${JSON.stringify({
              type: "chunk",
              content: chunk,
              fullText: accumulatedText,
            })}\n\n`
          );
        },
        () => {
          controller.enqueue(
            `data: ${JSON.stringify({
              type: "complete",
              content: accumulatedText,
            })}\n\n`
          );
          controller.close();
        }
      );
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

export async function OPTIONS() {
  return new Response(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}