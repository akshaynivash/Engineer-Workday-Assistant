import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError, sendChat } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function QuickChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [unavailable, setUnavailable] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  const handleSend = () => {
    const message = input.trim();
    if (!message) return;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setSending(true);
    sendChat(message)
      .then((res) => setMessages((prev) => [...prev, { role: "assistant", content: res.response }]))
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 503) {
          setUnavailable(error.message);
        } else {
          setUnavailable("⚠️ Could not reach the backend. Is it running?");
        }
      })
      .finally(() => setSending(false));
  };

  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h2 className="text-2xl font-bold">💬 Quick Chat</h2>
        <p className="text-muted-foreground text-sm mt-1">
          General conversation — not for finding parts (use 🔩 Part Sourcing for that) or task/schedule/meal help
          (use 🗓️ Workday Help). Just casual chat, powered by a locally running Ollama model.
        </p>
      </div>

      {unavailable && (
        <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          ⚠️ Quick Chat is unavailable — it needs a locally running Ollama with a model pulled (default:{" "}
          <code>mistral</code>). Run <code>ollama pull mistral</code>, or set <code>OLLAMA_CHAT_MODEL</code> to a
          model you already have. The rest of the app works fine without this.
          <p className="mt-1 text-xs opacity-80">Details: {unavailable}</p>
        </div>
      )}

      <div className="border rounded-md p-4 space-y-3 min-h-[16rem]">
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
            <span
              className={
                m.role === "user"
                  ? "inline-block rounded-md bg-primary text-primary-foreground px-3 py-2 text-sm"
                  : "inline-block rounded-md bg-muted px-3 py-2 text-sm"
              }
            >
              {m.content}
            </span>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="What is up?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={sending}
        />
        <Button onClick={handleSend} disabled={sending}>
          Send
        </Button>
      </div>
    </div>
  );
}
