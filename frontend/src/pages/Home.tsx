import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const TOOLS = [
  {
    icon: "🔩",
    title: "Part Sourcing",
    accent: "border-t-4 border-t-amber-500",
    description:
      "You have a fuse's part ID and it's unavailable, discontinued, or doesn't quite meet spec — find a suitable replacement.",
    points: [
      "Enter a part ID (e.g. A001)",
      "See its specs and a physics-based explanation",
      "Get ranked alternatives, loosest-to-strictest match",
      "Not sure which ID to try? The page has a browse/search panel.",
    ],
  },
  {
    icon: "💬",
    title: "Quick Chat",
    accent: "border-t-4 border-t-sky-500",
    description:
      "General conversation, unrelated to the other tools — for quick questions or just talking through something while you work. Powered by a locally running Ollama model, no cloud API key needed.",
    points: ["Casual chat", "Runs on your own machine via Ollama", "For part lookups or workday help, use the other pages"],
  },
  {
    icon: "🗓️",
    title: "Workday Help",
    accent: "border-t-4 border-t-emerald-500",
    description:
      "The rest of your workday: keep track of your schedule, plan meals, and get study help on material you've indexed. Understands natural phrasing, not just exact keywords.",
    points: [
      '"What\'s my Monday schedule?"',
      '"Plan my meals for this week"',
      '"Explain today\'s topic from the PDF"',
      "Also tracks daily check-in tasks",
    ],
  },
];

export default function Home() {
  return (
    <div className="max-w-5xl">
      <h2 className="text-3xl font-bold flex items-center gap-2 text-primary">🛠️ Engineer's Workday Assistant</h2>
      <p className="text-muted-foreground mt-2 max-w-2xl">
        Three tools at one workbench, for whatever your workday throws at you. Pick whichever one fits the moment —
        none of them is the "main" one. Here's what each is for.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        {TOOLS.map((tool) => (
          <Card key={tool.title} className={tool.accent}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span>{tool.icon}</span> {tool.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm">{tool.description}</p>
              <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                {tool.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="text-xs text-muted-foreground mt-8">
        Quick Chat and Workday Help need extra models/services set up locally (see README) — if they're not
        available, you'll see a friendly note instead of a crash, and the rest of the app keeps working.
      </p>
    </div>
  );
}
