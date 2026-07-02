import { useEffect, useState } from "react";
import { Search, ChevronDown, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  ApiError,
  explainPart,
  getAlternatives,
  getPart,
  getPartFacets,
  browseParts,
  type PartDetail,
  type PartFacets,
  type PartSummary,
  type Tier,
} from "@/lib/api";

const ANY = "Any";

export default function PartSourcing() {
  const [useAi, setUseAi] = useState(false);
  const [browseOpen, setBrowseOpen] = useState(false);

  const [facets, setFacets] = useState<PartFacets | null>(null);
  const [applicationFilter, setApplicationFilter] = useState(ANY);
  const [fuseTypeFilter, setFuseTypeFilter] = useState(ANY);
  const [browseResults, setBrowseResults] = useState<PartSummary[]>([]);

  const [productId, setProductId] = useState("");
  const [searchedId, setSearchedId] = useState<string | null>(null);
  const [selectedPart, setSelectedPart] = useState<PartDetail | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  const [tier, setTier] = useState<Tier>("Tier 1");
  const [alternatives, setAlternatives] = useState<PartSummary[]>([]);
  const [physicsExplanation, setPhysicsExplanation] = useState("");
  const [altExplanations, setAltExplanations] = useState<Record<string, string>>({});
  const [loadingAlternatives, setLoadingAlternatives] = useState(false);

  useEffect(() => {
    getPartFacets()
      .then(setFacets)
      .catch(() => setFacets(null));
  }, []);

  useEffect(() => {
    let ignore = false;
    browseParts({
      application: applicationFilter === ANY ? undefined : applicationFilter,
      fuseType: fuseTypeFilter === ANY ? undefined : fuseTypeFilter,
      limit: 20,
    })
      .then((results) => !ignore && setBrowseResults(results))
      .catch(() => !ignore && setBrowseResults([]));
    return () => {
      ignore = true;
    };
  }, [applicationFilter, fuseTypeFilter]);

  const handleSearch = () => {
    const id = productId.trim();
    if (!id) return;
    setSearchedId(id);
    setSearchError(null);
    setSelectedPart(null);
    setTier("Tier 1");
    getPart(id)
      .then(setSelectedPart)
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 404) {
          setSearchError("⚠️ Product ID not found in database. Use the browse/search panel above to find a valid ID.");
        } else {
          setSearchError("⚠️ Could not reach the backend. Is it running?");
        }
      });
  };

  useEffect(() => {
    if (!selectedPart) return;
    let ignore = false;
    explainPart(selectedPart.ID, { useAi, alternativeId: null })
      .then((res) => !ignore && setPhysicsExplanation(res.explanation))
      .catch(() => !ignore && setPhysicsExplanation("Could not load explanation."));
    return () => {
      ignore = true;
    };
  }, [selectedPart, useAi]);

  useEffect(() => {
    if (!selectedPart) return;
    let ignore = false;
    setLoadingAlternatives(true);
    getAlternatives(selectedPart.ID, tier)
      .then(async (alts) => {
        if (ignore) return;
        setAlternatives(alts);
        const entries = await Promise.all(
          alts.map(async (alt) => {
            const res = await explainPart(selectedPart.ID, { useAi, alternativeId: alt.ID });
            return [alt.ID, res.explanation] as const;
          }),
        );
        if (!ignore) setAltExplanations(Object.fromEntries(entries));
      })
      .finally(() => !ignore && setLoadingAlternatives(false));
    return () => {
      ignore = true;
    };
  }, [selectedPart, tier, useAi]);

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold">🔩 Part Sourcing</h2>
        <p className="text-muted-foreground text-sm mt-1">
          Have a fuse's part ID that's out of stock, discontinued, or not quite the right spec? Enter it below to
          see its details and get ranked alternatives.
        </p>
      </div>

      <div className="flex items-center gap-2">
        <Checkbox id="use-ai" checked={useAi} onCheckedChange={(v) => setUseAi(v === true)} />
        <Label htmlFor="use-ai">🤖 Use AI-generated explanations (Phi-1.5)</Label>
      </div>

      <Card>
        <CardHeader className="cursor-pointer" onClick={() => setBrowseOpen((o) => !o)}>
          <CardTitle className="flex items-center gap-2 text-base">
            {browseOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            🔎 Not sure which ID to try? Browse or search the catalog
          </CardTitle>
        </CardHeader>
        {browseOpen && (
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Application</Label>
                <Select value={applicationFilter} onValueChange={setApplicationFilter}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ANY}>Any</SelectItem>
                    {facets?.applications.map((app) => (
                      <SelectItem key={app} value={app}>
                        {app}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Fuse type</Label>
                <Select value={fuseTypeFilter} onValueChange={setFuseTypeFilter}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ANY}>Any</SelectItem>
                    {facets?.fuse_types.map((ft) => (
                      <SelectItem key={ft} value={ft}>
                        {ft}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              {browseResults.length} matching part(s) — copy an ID below into the search box:
            </p>
            <div className="border rounded-md divide-y max-h-64 overflow-y-auto">
              {browseResults.map((part) => (
                <div key={part.ID} className="p-2 text-sm flex justify-between gap-2">
                  <span className="font-mono">{part.ID}</span>
                  <span className="text-muted-foreground flex-1">{part.DESCRIPTION}</span>
                  <span className="text-muted-foreground">{part.Application}</span>
                  <span className="text-muted-foreground">{part.Attribut1}</span>
                </div>
              ))}
            </div>
          </CardContent>
        )}
      </Card>

      <div className="flex gap-2">
        <Input
          placeholder="e.g. A001"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />
        <Button onClick={handleSearch}>
          <Search className="h-4 w-4 mr-1" /> Find alternatives
        </Button>
      </div>

      {searchError && searchedId && <p className="text-sm text-destructive">{searchError}</p>}

      {selectedPart && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">📌 Product Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>
                🔹 <strong>{selectedPart.DESCRIPTION}</strong>
              </p>
              <p>🔬 <strong>Physics-Based Explanation:</strong></p>
              <p className="text-muted-foreground">{physicsExplanation}</p>
              <p>
                ⚡ <strong>Rated Current:</strong> {selectedPart["Rated Current (A)"]}A,{" "}
                <strong>Rated Voltage:</strong> {selectedPart["Rated Voltage (V)"]}V
              </p>
              <p>
                🔥 <strong>Breaking Capacity:</strong> {selectedPart["Rated Breaking Capacity (A)"]}A,{" "}
                <strong>Mounting:</strong> {selectedPart.Mounting}
              </p>
            </CardContent>
          </Card>

          <div>
            <h3 className="font-semibold mb-2">✅ Alternative Products & Justification:</h3>
            {loadingAlternatives && <p className="text-sm text-muted-foreground">Loading alternatives…</p>}
            {!loadingAlternatives && alternatives.length === 0 && (
              <p className="text-sm text-muted-foreground">⚠️ No suitable alternatives found.</p>
            )}
            <div className="space-y-3">
              {alternatives.map((alt) => (
                <Card key={alt.ID}>
                  <CardContent className="p-4 text-sm space-y-1">
                    <p>
                      🔹 <strong>
                        [{alt.ID}] {alt.DESCRIPTION}
                      </strong>
                    </p>
                    <p className="text-muted-foreground">💡 {altExplanations[alt.ID] ?? "Loading…"}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {!loadingAlternatives && alternatives.length < 5 && (
              <div className="mt-4 space-y-2">
                <p className="text-sm">🔔 Fewer than 5 alternatives found. You can relax constraints further:</p>
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm" onClick={() => setTier("Tier 3")}>
                    Relax Current Tolerance (±5A)
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setTier("Tier 4")}>
                    Allow Different Mounting Styles
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setTier("Tier 5")}>
                    Allow Different Fuse Types
                  </Button>
                </div>
              </div>
            )}

            <div className="mt-6 text-sm space-y-1">
              <h4 className="font-semibold">⚖️ Why Are Some Relaxations Allowed?</h4>
              <p className="text-muted-foreground">
                ➡️ In some cases, exact matches are not available, so the following relaxations are considered:
              </p>
              <p className="text-muted-foreground">
                ✔️ <strong>Voltage Relaxation (±10%)</strong> → Allows alternatives within an acceptable range to
                function safely.
              </p>
              <p className="text-muted-foreground">
                ✔️ <strong>Breaking Capacity Tolerance</strong> → Small deviations are permitted if they don't
                impact circuit safety.
              </p>
              <p className="text-muted-foreground">
                ✔️ <strong>Mechanical Fitment Adjustments</strong> → If functionally compatible, slight variations
                in mounting style may be acceptable.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
