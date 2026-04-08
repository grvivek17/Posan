import { useState, useCallback } from "react";
import { Upload, FileText, Trash2, User, Mail, Phone, ChevronDown, ChevronUp, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { uploadResume, listProfiles, deleteProfile } from "@/lib/api";

interface SkillItem {
  name: string;
  level: string;
  years?: number | null;
}

interface SkillCategory {
  category: string;
  skills: SkillItem[];
}

interface SkillMatrix {
  name?: string;
  email?: string;
  phone?: string;
  summary?: string;
  skills?: SkillCategory[];
  experience_years?: number;
  education?: { degree: string; institution: string; year: string }[];
  certifications?: string[];
}

interface Profile {
  id: number;
  name: string;
  email: string;
  phone: string;
  filename: string;
  skill_matrix: SkillMatrix;
  created_at: string;
}

function getLevelColor(level: string) {
  switch (level?.toLowerCase()) {
    case "expert": return "bg-green-100 text-green-800 border-green-300";
    case "advanced": return "bg-blue-100 text-blue-800 border-blue-300";
    case "intermediate": return "bg-yellow-100 text-yellow-800 border-yellow-300";
    case "beginner": return "bg-gray-100 text-gray-800 border-gray-300";
    default: return "bg-gray-100 text-gray-700 border-gray-300";
  }
}

export default function ResumeUpload() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [loaded, setLoaded] = useState(false);

  const loadProfiles = useCallback(async () => {
    try {
      const data = await listProfiles();
      setProfiles(data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  if (!loaded) {
    setLoaded(true);
    loadProfiles();
  }

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        await uploadResume(files[i]);
      }
      await loadProfiles();
    } catch (e) {
      console.error(e);
      alert("Upload failed: " + (e instanceof Error ? e.message : "Unknown error"));
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this profile?")) return;
    try {
      await deleteProfile(id);
      await loadProfiles();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleUpload(e.dataTransfer.files);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Resume Upload</h1>
        <p className="text-muted-foreground mt-1">Upload resumes to automatically generate AI-powered skill matrices</p>
      </div>

      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {uploading ? (
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-12 w-12 text-primary animate-spin" />
                <p className="text-lg font-medium">Analyzing resume with AI...</p>
                <p className="text-sm text-muted-foreground">Extracting skills and generating matrix</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <Upload className="h-12 w-12 text-muted-foreground" />
                <p className="text-lg font-medium">Drag & drop resumes here</p>
                <p className="text-sm text-muted-foreground">Supports PDF and DOC/DOCX files</p>
                <label>
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.doc,.docx"
                    multiple
                    onChange={(e) => handleUpload(e.target.files)}
                  />
                  <Button variant="outline" className="mt-2" asChild>
                    <span>Browse Files</span>
                  </Button>
                </label>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Profiles List */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Uploaded Profiles ({profiles.length})</h2>
        {profiles.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No profiles yet. Upload a resume to get started.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {profiles.map((profile) => (
              <Card key={profile.id} className="overflow-hidden">
                <CardHeader
                  className="cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => setExpandedId(expandedId === profile.id ? null : profile.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{profile.name}</CardTitle>
                        <CardDescription className="flex items-center gap-4 mt-1">
                          {profile.email && (
                            <span className="flex items-center gap-1">
                              <Mail className="h-3 w-3" /> {profile.email}
                            </span>
                          )}
                          {profile.phone && (
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" /> {profile.phone}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <FileText className="h-3 w-3" /> {profile.filename}
                          </span>
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(profile.id);
                        }}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                      {expandedId === profile.id ? (
                        <ChevronUp className="h-5 w-5 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                  </div>
                </CardHeader>

                {expandedId === profile.id && profile.skill_matrix && (
                  <CardContent className="border-t bg-muted/20">
                    <div className="space-y-4 pt-4">
                      {/* Summary */}
                      {profile.skill_matrix.summary && (
                        <div>
                          <h4 className="font-medium text-sm text-muted-foreground mb-1">Professional Summary</h4>
                          <p className="text-sm">{profile.skill_matrix.summary}</p>
                        </div>
                      )}

                      {/* Experience */}
                      {profile.skill_matrix.experience_years && (
                        <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-3 py-1 rounded-full text-sm font-medium">
                          {profile.skill_matrix.experience_years} years of experience
                        </div>
                      )}

                      {/* Skills Matrix */}
                      {profile.skill_matrix.skills && profile.skill_matrix.skills.length > 0 && (
                        <div>
                          <h4 className="font-medium text-sm text-muted-foreground mb-2">Skill Matrix</h4>
                          <div className="space-y-3">
                            {profile.skill_matrix.skills.map((cat, i) => (
                              <div key={i}>
                                <p className="text-sm font-medium mb-1.5">{cat.category}</p>
                                <div className="flex flex-wrap gap-2">
                                  {cat.skills.map((skill, j) => (
                                    <span
                                      key={j}
                                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${getLevelColor(skill.level)}`}
                                    >
                                      {skill.name}
                                      <span className="opacity-75">({skill.level})</span>
                                      {skill.years && <span className="opacity-60">{skill.years}y</span>}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Education */}
                      {profile.skill_matrix.education && profile.skill_matrix.education.length > 0 && (
                        <div>
                          <h4 className="font-medium text-sm text-muted-foreground mb-1">Education</h4>
                          <div className="space-y-1">
                            {profile.skill_matrix.education.map((edu, i) => (
                              <p key={i} className="text-sm">
                                {edu.degree} - {edu.institution} {edu.year && `(${edu.year})`}
                              </p>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Certifications */}
                      {profile.skill_matrix.certifications && profile.skill_matrix.certifications.length > 0 && (
                        <div>
                          <h4 className="font-medium text-sm text-muted-foreground mb-1">Certifications</h4>
                          <div className="flex flex-wrap gap-2">
                            {profile.skill_matrix.certifications.map((cert, i) => (
                              <span key={i} className="bg-secondary text-secondary-foreground px-2.5 py-1 rounded-md text-xs">
                                {cert}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
