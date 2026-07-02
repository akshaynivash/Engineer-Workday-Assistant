import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ApiError, createTask, getRecentTasks, sendAssistantChat } from "@/lib/api";

const DAILY_TASKS = [
  "Complete Duolingo",
  "Take vitamins",
  "Drink 3 L water",
  "Snapscore check",
  "Prepare a topic for stat exam",
  "Surf new tech update",
  "Good moment of a day",
  "Bad moment of a day",
  "Today's affirmation",
];

interface Message {
  role: "user" | "assistant";
  content: string;
}

function AssistantChat() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hello! How are you doing today? How may I assist you?" },
  ]);
  const [input, setInput] = useState("");
  const [unavailable, setUnavailable] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  const handleSend = () => {
    const message = input.trim();
    if (!message) return;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setInput("");
    setSending(true);
    sendAssistantChat(message)
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
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Try: <em>"What's my schedule for Monday?"</em> · <em>"Plan my meals for this week"</em> ·{" "}
        <em>"Explain today's topic from the study material"</em> · or just say hi.
      </p>

      {unavailable && (
        <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          ⚠️ Workday Help is unavailable — it needs a locally running Ollama with a tool-calling-capable model
          pulled. The rest of the app works fine without this.
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

function DailyTasks() {
  const [singleTask, setSingleTask] = useState("");
  const [singleAnswer, setSingleAnswer] = useState("");
  const [singleDay, setSingleDay] = useState("");
  const [singleStatus, setSingleStatus] = useState<string | null>(null);

  const [dayForAll, setDayForAll] = useState("");
  const [bulkAnswers, setBulkAnswers] = useState<Record<string, string>>({});
  const [bulkStatus, setBulkStatus] = useState<string | null>(null);

  const [recentTasks, setRecentTasks] = useState<string[] | null>(null);

  const handleSaveSingle = () => {
    if (!singleTask || !singleAnswer) {
      setSingleStatus("Please provide both a task and an answer.");
      return;
    }
    createTask({ task: singleTask, answer: singleAnswer, day: singleDay || null })
      .then((res) => setSingleStatus(res.message))
      .catch(() => setSingleStatus("Could not save — is the backend running?"));
  };

  const handleSaveAll = async () => {
    const entries = Object.entries(bulkAnswers).filter(([, answer]) => answer.trim());
    for (const [task, answer] of entries) {
      await createTask({ task, answer, day: dayForAll || null }).catch(() => null);
    }
    setBulkStatus("All entered tasks have been saved!");
  };

  const handleShowRecent = () => {
    getRecentTasks(5)
      .then(setRecentTasks)
      .catch(() => setRecentTasks([]));
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="font-semibold mb-2">Store a Single Task</h3>
        <div className="space-y-2 max-w-md">
          <Input placeholder="Task" value={singleTask} onChange={(e) => setSingleTask(e.target.value)} />
          <Input placeholder="Answer" value={singleAnswer} onChange={(e) => setSingleAnswer(e.target.value)} />
          <Input
            placeholder="Day (YYYY-MM-DD)"
            value={singleDay}
            onChange={(e) => setSingleDay(e.target.value)}
          />
          <Button onClick={handleSaveSingle}>Save Single Task</Button>
          {singleStatus && <p className="text-sm text-muted-foreground">{singleStatus}</p>}
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Store Multiple Daily Tasks</h3>
        <div className="space-y-2 max-w-md">
          <Input
            placeholder="Day for all tasks (YYYY-MM-DD)"
            value={dayForAll}
            onChange={(e) => setDayForAll(e.target.value)}
          />
          {DAILY_TASKS.map((task) => (
            <div key={task}>
              <Label className="text-xs">{task}</Label>
              <Input
                value={bulkAnswers[task] ?? ""}
                onChange={(e) => setBulkAnswers((prev) => ({ ...prev, [task]: e.target.value }))}
              />
            </div>
          ))}
          <Button onClick={handleSaveAll}>Save All Listed Tasks</Button>
          {bulkStatus && <p className="text-sm text-muted-foreground">{bulkStatus}</p>}
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-2">Show Recent Tasks</h3>
        <Button variant="outline" onClick={handleShowRecent}>
          Show Recent 5 Tasks
        </Button>
        {recentTasks !== null && (
          <div className="mt-3 space-y-2 text-sm whitespace-pre-wrap">
            {recentTasks.length === 0 ? (
              <p className="text-muted-foreground">No tasks found.</p>
            ) : (
              recentTasks.map((task, i) => (
                <div key={i} className="border rounded-md p-2">
                  {task}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function WorkdayHelp() {
  return (
    <div className="max-w-2xl space-y-4">
      <div>
        <h2 className="text-2xl font-bold">🗓️ Workday Help</h2>
        <p className="text-muted-foreground text-sm mt-1">
          Ask about your schedule, get a meal plan, get study help on indexed material, or just chat — a LangChain
          agent figures out which of those you mean instead of relying on exact keywords.
        </p>
      </div>

      <Tabs defaultValue="chat">
        <TabsList>
          <TabsTrigger value="chat">Chat</TabsTrigger>
          <TabsTrigger value="tasks">Daily Tasks</TabsTrigger>
        </TabsList>
        <TabsContent value="chat">
          <AssistantChat />
        </TabsContent>
        <TabsContent value="tasks">
          <DailyTasks />
        </TabsContent>
      </Tabs>
    </div>
  );
}
