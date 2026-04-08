import { useState, useCallback } from "react";
import {
  Plus,
  Edit2,
  Trash2,
  ClipboardList,
  Users,
  Loader2,
  Search,
  UserCheck,
  Mail,
  Phone,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  listRequirements,
  createRequirement,
  updateRequirement,
  deleteRequirement,
  matchProfilesForRequirement,
} from "@/lib/api";

interface Requirement {
  id: number;
  req_code: string;
  title: string;
  description: string;
  skills_needed: string;
  team_size: number;
  status: string;
  created_at: string;
}

interface MatchedProfile {
  profile_id: number;
  name: string;
  email: string;
  phone: string;
  similarity: number;
  top_skills: string[];
}

const statusColors: Record<string, string> = {
  open: "bg-green-100 text-green-800",
  "in-progress": "bg-blue-100 text-blue-800",
  closed: "bg-gray-100 text-gray-800",
  filled: "bg-purple-100 text-purple-800",
};

export default function Requirements() {
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Requirement | null>(null);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Profile matching state
  const [matchedProfiles, setMatchedProfiles] = useState<MatchedProfile[]>([]);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchPanelOpen, setMatchPanelOpen] = useState(false);
  const [matchReqTitle, setMatchReqTitle] = useState("");

  const [form, setForm] = useState({
    title: "",
    description: "",
    skills_needed: "",
    team_size: 1,
    status: "open",
  });

  const loadRequirements = useCallback(async () => {
    try {
      const data = await listRequirements();
      setRequirements(data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  if (!loaded) {
    setLoaded(true);
    loadRequirements();
  }

  const openCreate = () => {
    setEditing(null);
    setForm({ title: "", description: "", skills_needed: "", team_size: 1, status: "open" });
    setDialogOpen(true);
  };

  const openEdit = (req: Requirement) => {
    setEditing(req);
    setForm({
      title: req.title,
      description: req.description || "",
      skills_needed: req.skills_needed || "",
      team_size: req.team_size,
      status: req.status,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      if (editing) {
        await updateRequirement(editing.id, form);
      } else {
        await createRequirement(form);
      }
      await loadRequirements();
      setDialogOpen(false);
    } catch (e) {
      console.error(e);
      alert("Failed to save: " + (e instanceof Error ? e.message : ""));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this requirement?")) return;
    try {
      await deleteRequirement(id);
      await loadRequirements();
    } catch (e) {
      console.error(e);
    }
  };

  const handleMatchProfiles = async (req: Requirement) => {
    setMatchReqTitle(`${req.req_code || ""} - ${req.title}`);
    setMatchLoading(true);
    setMatchPanelOpen(true);
    setMatchedProfiles([]);
    try {
      const data = await matchProfilesForRequirement(req.id);
      setMatchedProfiles(data.matched_profiles || []);
    } catch (e) {
      console.error(e);
      alert("Failed to find matching profiles: " + (e instanceof Error ? e.message : ""));
    } finally {
      setMatchLoading(false);
    }
  };

  const filtered = requirements.filter(
    (r) =>
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.skills_needed?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.req_code?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Requirements</h1>
          <p className="text-muted-foreground mt-1">Manage talent requirements and track hiring needs</p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="h-4 w-4 mr-2" />
          New Requirement
        </Button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search requirements..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {filtered.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center text-muted-foreground">
            <ClipboardList className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>{requirements.length === 0 ? "No requirements yet. Create one to get started." : "No matching requirements found."}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((req) => (
            <Card key={req.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {req.req_code && (
                      <span className="text-xs font-mono font-bold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded">
                        {req.req_code}
                      </span>
                    )}
                    <CardTitle className="text-base leading-tight">{req.title}</CardTitle>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ml-2 ${statusColors[req.status] || "bg-gray-100 text-gray-700"}`}
                  >
                    {req.status}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                {req.description && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{req.description}</p>
                )}
                {req.skills_needed && (
                  <div className="mb-3">
                    <p className="text-xs font-medium text-muted-foreground mb-1">Skills Needed</p>
                    <div className="flex flex-wrap gap-1">
                      {req.skills_needed.split(",").map((skill, i) => (
                        <span
                          key={i}
                          className="bg-secondary text-secondary-foreground text-xs px-2 py-0.5 rounded"
                        >
                          {skill.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex items-center justify-between mt-4">
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <span>Team Size: {req.team_size}</span>
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Find Matching Profiles"
                      onClick={() => handleMatchProfiles(req)}
                    >
                      <UserCheck className="h-4 w-4 text-indigo-600" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => openEdit(req)}>
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(req.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Matched Profiles Panel */}
      <Dialog open={matchPanelOpen} onOpenChange={setMatchPanelOpen}>
        <DialogContent className="sm:max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <UserCheck className="h-5 w-5 text-indigo-600" />
              Matching Profiles
            </DialogTitle>
            <DialogDescription>
              Profiles matching: <span className="font-semibold">{matchReqTitle}</span>
            </DialogDescription>
          </DialogHeader>

          {matchLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
              <span className="ml-3 text-muted-foreground">Finding matching profiles...</span>
            </div>
          ) : matchedProfiles.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <UserCheck className="h-12 w-12 mx-auto mb-3 opacity-40" />
              <p className="font-medium">No matching profiles found</p>
              <p className="text-sm mt-1">Try adjusting the skills in this requirement</p>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Found {matchedProfiles.length} matching profile{matchedProfiles.length !== 1 ? "s" : ""}
              </p>
              {matchedProfiles.map((profile, idx) => (
                <Card key={profile.profile_id} className="border">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-bold bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                            #{idx + 1}
                          </span>
                          <h4 className="font-semibold text-base">{profile.name}</h4>
                          <span
                            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                              profile.similarity >= 0.5
                                ? "bg-green-100 text-green-700"
                                : profile.similarity >= 0.3
                                ? "bg-yellow-100 text-yellow-700"
                                : "bg-orange-100 text-orange-700"
                            }`}
                          >
                            {Math.round(profile.similarity * 100)}% match
                          </span>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                          {profile.email && (
                            <span className="flex items-center gap-1">
                              <Mail className="h-3 w-3" />
                              {profile.email}
                            </span>
                          )}
                          {profile.phone && (
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {profile.phone}
                            </span>
                          )}
                        </div>

                        {profile.top_skills.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {profile.top_skills.map((skill, si) => (
                              <span
                                key={si}
                                className="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Match quality bar */}
                    <div className="mt-3">
                      <div className="w-full bg-gray-100 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full ${
                            profile.similarity >= 0.5
                              ? "bg-green-500"
                              : profile.similarity >= 0.3
                              ? "bg-yellow-500"
                              : "bg-orange-500"
                          }`}
                          style={{ width: `${Math.round(profile.similarity * 100)}%` }}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit Requirement" : "New Requirement"}</DialogTitle>
            <DialogDescription>
              {editing ? "Update the requirement details below." : "Fill in the details for the new requirement."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="e.g., Frontend Development Team"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Describe the requirement..."
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="skills">Skills Needed (comma separated)</Label>
              <Input
                id="skills"
                value={form.skills_needed}
                onChange={(e) => setForm({ ...form, skills_needed: e.target.value })}
                placeholder="e.g., React, TypeScript, Node.js"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="teamSize">Team Size</Label>
                <Input
                  id="teamSize"
                  type="number"
                  min={1}
                  value={form.team_size}
                  onChange={(e) => setForm({ ...form, team_size: parseInt(e.target.value) || 1 })}
                />
              </div>
              <div>
                <Label>Status</Label>
                <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in-progress">In Progress</SelectItem>
                    <SelectItem value="filled">Filled</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving || !form.title.trim()}>
              {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              {editing ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
