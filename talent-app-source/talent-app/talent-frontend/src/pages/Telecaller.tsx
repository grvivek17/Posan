import { useState, useCallback, useEffect, useRef } from "react";
import {
  Phone,
  PhoneCall,
  PhoneOff,
  Plus,
  Trash2,
  Play,
  CheckCircle,
  Loader2,
  MessageSquare,
  ClipboardList,
  Wifi,
  WifiOff,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { Input } from "@/components/ui/input";
import {
  listQuestions,
  createQuestion,
  deleteQuestion,
  createCall,
  listCalls,
  listProfiles,
  listRequirements,
  submitBulkResponses,
  getTwilioStatus,
  createTwilioCall,
  getCallStatus,
} from "@/lib/api";

interface Question {
  id: number;
  requirement_id: number | null;
  question: string;
  question_order: number;
}

interface CallResponse {
  id: number;
  question_id: number;
  response: string;
  question?: string;
}

interface Call {
  id: number;
  profile_id: number;
  profile_name: string;
  profile_email: string;
  profile_phone: string;
  requirement_id: number | null;
  status: string;
  responses: CallResponse[];
  created_at: string;
  twilio_sid?: string;
  twilio_status?: string;
  call_duration?: number;
  recording_url?: string;
  phone_number?: string;
}

interface Profile {
  id: number;
  name: string;
  email: string;
  phone: string;
}

interface Requirement {
  id: number;
  title: string;
}

export default function Telecaller() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [calls, setCalls] = useState<Call[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [requirements, setRequirements] = useState<Requirement[]>([]);
  const [loaded, setLoaded] = useState(false);

  // Dialog state
  const [questionDialogOpen, setQuestionDialogOpen] = useState(false);
  const [callDialogOpen, setCallDialogOpen] = useState(false);
  const [activeCallDialog, setActiveCallDialog] = useState(false);
  const [newQuestion, setNewQuestion] = useState("");
  const [selectedReqForQ, setSelectedReqForQ] = useState<string>("none");
  const [selectedProfile, setSelectedProfile] = useState<string>("");
  const [selectedReqForCall, setSelectedReqForCall] = useState<string>("none");
  const [creatingCall, setCreatingCall] = useState(false);

  // Active call state
  const [activeCall, setActiveCall] = useState<{
    call_id: number;
    profile: Profile;
    questions: Question[];
    script: string;
  } | null>(null);
  const [callResponses, setCallResponses] = useState<Record<number, string>>({});
  const [submittingCall, setSubmittingCall] = useState(false);

  // Twilio state
  const [twilioConfigured, setTwilioConfigured] = useState(false);
  const [twilioCallDialogOpen, setTwilioCallDialogOpen] = useState(false);
  const [twilioPhoneNumber, setTwilioPhoneNumber] = useState("");
  const [twilioCallingProfile, setTwilioCallingProfile] = useState<Profile | null>(null);
  const [twilioCallInProgress, setTwilioCallInProgress] = useState(false);
  const [twilioActiveCallId, setTwilioActiveCallId] = useState<number | null>(null);
  const [twilioCallStatus, setTwilioCallStatus] = useState<string>("");
  const [twilioCallResponses, setTwilioCallResponses] = useState<CallResponse[]>([]);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [q, c, p, r, ts] = await Promise.all([
        listQuestions(),
        listCalls(),
        listProfiles(),
        listRequirements(),
        getTwilioStatus().catch(() => ({ configured: false })),
      ]);
      setQuestions(q);
      setCalls(c);
      setProfiles(p);
      setRequirements(r);
      setTwilioConfigured(ts.configured);
    } catch (e) {
      console.error(e);
    }
  }, []);

  if (!loaded) {
    setLoaded(true);
    loadData();
  }

  const handleAddQuestion = async () => {
    if (!newQuestion.trim()) return;
    try {
      await createQuestion({
        question: newQuestion,
        requirement_id: selectedReqForQ !== "none" ? parseInt(selectedReqForQ) : undefined,
        question_order: questions.length,
      });
      setNewQuestion("");
      setQuestionDialogOpen(false);
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteQuestion = async (id: number) => {
    try {
      await deleteQuestion(id);
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartCall = async () => {
    if (!selectedProfile) return;
    setCreatingCall(true);
    try {
      const data = await createCall({
        profile_id: parseInt(selectedProfile),
        requirement_id: selectedReqForCall !== "none" ? parseInt(selectedReqForCall) : undefined,
      });
      setActiveCall(data);
      setCallResponses({});
      setCallDialogOpen(false);
      setActiveCallDialog(true);
      await loadData();
    } catch (e) {
      console.error(e);
      alert("Failed to start call: " + (e instanceof Error ? e.message : ""));
    } finally {
      setCreatingCall(false);
    }
  };

  const handleSubmitResponses = async () => {
    if (!activeCall) return;
    setSubmittingCall(true);
    try {
      const responses = activeCall.questions.map((q) => ({
        question_id: q.id,
        response: callResponses[q.id] || "",
      }));
      await submitBulkResponses({ call_id: activeCall.call_id, responses });
      setActiveCallDialog(false);
      setActiveCall(null);
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setSubmittingCall(false);
    }
  };

  // Twilio call handlers
  const handleStartTwilioCall = async () => {
    if (!twilioCallingProfile || !twilioPhoneNumber.trim()) return;
    setTwilioCallInProgress(true);
    try {
      const data = await createTwilioCall({
        profile_id: twilioCallingProfile.id,
        requirement_id: selectedReqForCall !== "none" ? parseInt(selectedReqForCall) : undefined,
        phone_number: twilioPhoneNumber.trim(),
      });
      setTwilioActiveCallId(data.call_id);
      setTwilioCallStatus("calling");
      setTwilioCallDialogOpen(false);
      // Start polling for status
      startPolling(data.call_id);
      await loadData();
    } catch (e) {
      alert("Failed to start Twilio call: " + (e instanceof Error ? e.message : ""));
      setTwilioCallInProgress(false);
    }
  };

  const startPolling = (callId: number) => {
    if (pollRef.current) clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const status = await getCallStatus(callId);
        setTwilioCallStatus(status.status);
        setTwilioCallResponses(status.responses || []);
        if (status.status === "completed" || status.status.startsWith("failed")) {
          if (pollRef.current) clearInterval(pollRef.current);
          pollRef.current = null;
          setTwilioCallInProgress(false);
          await loadData();
        }
      } catch {
        // Ignore polling errors
      }
    }, 3000);
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
          <Phone className="h-8 w-8 text-primary" />
          Telecaller
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage screening questions, make calls, and collect responses
        </p>
      </div>

      <Tabs defaultValue="questions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="questions" className="gap-2">
            <ClipboardList className="h-4 w-4" />
            Questions
          </TabsTrigger>
          <TabsTrigger value="calls" className="gap-2">
            <Phone className="h-4 w-4" />
            Calls
          </TabsTrigger>
          <TabsTrigger value="history" className="gap-2">
            <MessageSquare className="h-4 w-4" />
            Call History
          </TabsTrigger>
        </TabsList>

        {/* Questions Tab */}
        <TabsContent value="questions">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Screening Questions</h2>
            <Button onClick={() => setQuestionDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Question
            </Button>
          </div>
          {questions.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <ClipboardList className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No questions yet. Add screening questions to use during calls.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {questions.map((q, i) => (
                <Card key={q.id}>
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-muted-foreground w-6">{i + 1}.</span>
                      <div>
                        <p className="text-sm font-medium">{q.question}</p>
                        {q.requirement_id && (
                          <p className="text-xs text-muted-foreground">
                            Requirement: {requirements.find((r) => r.id === q.requirement_id)?.title || `#${q.requirement_id}`}
                          </p>
                        )}
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => handleDeleteQuestion(q.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Calls Tab */}
        <TabsContent value="calls">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Start a New Call</h2>
            <Button
              onClick={() => {
                setSelectedProfile("");
                setSelectedReqForCall("none");
                setCallDialogOpen(true);
              }}
              disabled={profiles.length === 0}
            >
              <Play className="h-4 w-4 mr-2" />
              Start Call
            </Button>
          </div>
          {profiles.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <Phone className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No profiles available. Upload resumes first to start making calls.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {profiles.map((p) => (
                <Card key={p.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">{p.name}</CardTitle>
                    <CardDescription>
                      {p.email && <span className="block">{p.email}</span>}
                      {p.phone && <span className="block">{p.phone}</span>}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex gap-2">
                    <Button
                      size="sm"
                      className="flex-1"
                      variant="outline"
                      onClick={() => {
                        setSelectedProfile(p.id.toString());
                        setSelectedReqForCall("none");
                        setCallDialogOpen(true);
                      }}
                    >
                      <Phone className="h-4 w-4 mr-2" />
                      Manual
                    </Button>
                    <Button
                      size="sm"
                      className="flex-1"
                      onClick={() => {
                        setTwilioCallingProfile(p);
                        setTwilioPhoneNumber(p.phone || "");
                        setSelectedReqForCall("none");
                        setTwilioCallDialogOpen(true);
                      }}
                      disabled={!twilioConfigured}
                      title={twilioConfigured ? "Make real call via Twilio" : "Twilio not configured"}
                    >
                      <PhoneCall className="h-4 w-4 mr-2" />
                      Twilio
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Twilio Status Banner */}
        {twilioConfigured && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2 text-sm text-green-800">
            <Wifi className="h-4 w-4" />
            Twilio is connected. You can make real automated calls.
          </div>
        )}
        {!twilioConfigured && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-center gap-2 text-sm text-yellow-800">
            <WifiOff className="h-4 w-4" />
            Twilio is not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER to enable automated calling. Manual call mode is available.
          </div>
        )}

        {/* Call History Tab */}
        <TabsContent value="history">
          <h2 className="text-lg font-semibold mb-4">Call History</h2>
          {calls.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No calls recorded yet.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {calls.map((call) => (
                <Card key={call.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{call.profile_name}</CardTitle>
                      <div className="flex items-center gap-2">
                        {call.twilio_sid && (
                          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                            Twilio
                          </span>
                        )}
                        <span
                          className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                            call.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : call.status.startsWith("failed")
                              ? "bg-red-100 text-red-800"
                              : call.status === "calling" || call.status === "in_progress"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {call.status}
                        </span>
                      </div>
                    </div>
                    <CardDescription>
                      {call.profile_email} {call.profile_phone && `| ${call.profile_phone}`}
                      <span className="block text-xs mt-1">{new Date(call.created_at).toLocaleString()}</span>
                    </CardDescription>
                  </CardHeader>
                  {call.responses && call.responses.length > 0 && (
                    <CardContent>
                      <div className="space-y-2">
                        {call.responses.map((r, i) => (
                          <div key={i} className="border rounded p-3 bg-muted/30">
                            <p className="text-xs font-medium text-muted-foreground mb-1">
                              Q: {r.question}
                            </p>
                            <p className="text-sm">{r.response || <span className="italic text-muted-foreground">No response</span>}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Add Question Dialog */}
      <Dialog open={questionDialogOpen} onOpenChange={setQuestionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Screening Question</DialogTitle>
            <DialogDescription>Create a new question for telecaller screening.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Question</Label>
              <Textarea
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                placeholder="e.g., What is your expected CTC?"
                rows={3}
              />
            </div>
            <div>
              <Label>Linked Requirement (optional)</Label>
              <Select value={selectedReqForQ} onValueChange={setSelectedReqForQ}>
                <SelectTrigger>
                  <SelectValue placeholder="Select requirement" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {requirements.map((r) => (
                    <SelectItem key={r.id} value={r.id.toString()}>
                      {r.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setQuestionDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleAddQuestion} disabled={!newQuestion.trim()}>Add Question</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Start Call Dialog */}
      <Dialog open={callDialogOpen} onOpenChange={setCallDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start Telecall</DialogTitle>
            <DialogDescription>Select a profile and optionally a requirement to start screening.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Profile</Label>
              <Select value={selectedProfile} onValueChange={setSelectedProfile}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a profile" />
                </SelectTrigger>
                <SelectContent>
                  {profiles.map((p) => (
                    <SelectItem key={p.id} value={p.id.toString()}>
                      {p.name} {p.email && `(${p.email})`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Requirement (optional)</Label>
              <Select value={selectedReqForCall} onValueChange={setSelectedReqForCall}>
                <SelectTrigger>
                  <SelectValue placeholder="Select requirement" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {requirements.map((r) => (
                    <SelectItem key={r.id} value={r.id.toString()}>
                      {r.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCallDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleStartCall} disabled={!selectedProfile || creatingCall}>
              {creatingCall && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              Start Call
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Twilio Call Dialog */}
      <Dialog open={twilioCallDialogOpen} onOpenChange={setTwilioCallDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <PhoneCall className="h-5 w-5 text-green-600" />
              Twilio Automated Call
            </DialogTitle>
            <DialogDescription>
              Make a real phone call to {twilioCallingProfile?.name}. The system will call the number, ask screening questions via text-to-speech, and record spoken responses.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Phone Number (E.164 format)</Label>
              <Input
                value={twilioPhoneNumber}
                onChange={(e) => setTwilioPhoneNumber(e.target.value)}
                placeholder="+1234567890"
              />
              <p className="text-xs text-muted-foreground mt-1">Include country code, e.g. +91 for India, +1 for US</p>
            </div>
            <div>
              <Label>Requirement (optional)</Label>
              <Select value={selectedReqForCall} onValueChange={setSelectedReqForCall}>
                <SelectTrigger>
                  <SelectValue placeholder="Select requirement" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {requirements.map((r) => (
                    <SelectItem key={r.id} value={r.id.toString()}>
                      {r.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded p-3">
              <p className="text-xs text-blue-800">
                <strong>{questions.length}</strong> screening question(s) will be asked via text-to-speech.
                {questions.length === 0 && " Add questions first before making a call."}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setTwilioCallDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleStartTwilioCall}
              disabled={!twilioPhoneNumber.trim() || questions.length === 0 || twilioCallInProgress}
            >
              {twilioCallInProgress ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <PhoneCall className="h-4 w-4 mr-2" />
              )}
              Call Now
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Twilio Call In Progress Dialog */}
      {twilioActiveCallId && twilioCallInProgress && (
        <Dialog open={true} onOpenChange={() => {}}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Phone className="h-5 w-5 text-green-600 animate-pulse" />
                Call In Progress
              </DialogTitle>
              <DialogDescription>
                Twilio is calling the candidate. Responses will appear here as they are collected.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-3 py-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Status:</span>
                <span className={`text-sm px-2 py-0.5 rounded-full ${
                  twilioCallStatus === "completed" ? "bg-green-100 text-green-800" :
                  twilioCallStatus === "in_progress" ? "bg-blue-100 text-blue-800" :
                  twilioCallStatus === "calling" ? "bg-yellow-100 text-yellow-800" :
                  "bg-gray-100 text-gray-800"
                }`}>{twilioCallStatus}</span>
              </div>
              {twilioCallResponses.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Responses Collected:</h4>
                  {twilioCallResponses.map((r, i) => (
                    <div key={i} className="border rounded p-3 bg-muted/30">
                      <p className="text-xs font-medium text-muted-foreground mb-1">Q: {r.question}</p>
                      <p className="text-sm">{r.response}</p>
                    </div>
                  ))}
                </div>
              )}
              {twilioCallResponses.length === 0 && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Waiting for responses...
                </div>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => {
                setTwilioActiveCallId(null);
                setTwilioCallInProgress(false);
                if (pollRef.current) clearInterval(pollRef.current);
                loadData();
              }}>
                <PhoneOff className="h-4 w-4 mr-2" />
                Dismiss
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Active Call Dialog */}
      <Dialog open={activeCallDialog} onOpenChange={setActiveCallDialog}>
        <DialogContent className="sm:max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Phone className="h-5 w-5 text-green-600" />
              Call with {activeCall?.profile.name}
            </DialogTitle>
            <DialogDescription>
              {activeCall?.profile.email} {activeCall?.profile.phone && `| ${activeCall.profile.phone}`}
            </DialogDescription>
          </DialogHeader>

          {activeCall && (
            <div className="space-y-4 py-2">
              {/* AI Script */}
              {activeCall.script && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-blue-800 mb-2">AI Call Script</h4>
                  <pre className="text-xs text-blue-700 whitespace-pre-wrap font-sans">{activeCall.script}</pre>
                </div>
              )}

              {/* Questions & Responses */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Record Responses</h4>
                {activeCall.questions.map((q, i) => (
                  <div key={q.id} className="border rounded-lg p-3">
                    <p className="text-sm font-medium mb-2">
                      {i + 1}. {q.question}
                    </p>
                    <Textarea
                      placeholder="Enter candidate's response..."
                      value={callResponses[q.id] || ""}
                      onChange={(e) =>
                        setCallResponses({ ...callResponses, [q.id]: e.target.value })
                      }
                      rows={2}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setActiveCallDialog(false)}>
              Cancel Call
            </Button>
            <Button onClick={handleSubmitResponses} disabled={submittingCall}>
              {submittingCall ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <CheckCircle className="h-4 w-4 mr-2" />
              )}
              Complete Call
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
