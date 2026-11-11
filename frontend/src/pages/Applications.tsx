import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Building2, MapPin, Calendar } from "lucide-react"

const placeholderJobs = [
  {
    id: 1,
    company: "Google",
    role: "Associate Cloud Engineer",
    location: "Bangalore, India",
    deadline: "Nov 25, 2026",
    status: "Applied",
  },
  {
    id: 2,
    company: "Microsoft",
    role: "Software Engineering Intern",
    location: "Hyderabad, India",
    deadline: "Dec 05, 2026",
    status: "Shortlisted",
  },
  {
    id: 3,
    company: "Amazon",
    role: "SDE-1 (Campus Hire)",
    location: "Bangalore, India",
    deadline: "Dec 12, 2026",
    status: "Interview Scheduled",
  },
]

export const Applications: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Placement Applications</h1>
          <p className="text-sm text-muted-foreground">
            View and manage your active campus job drives and internship applications.
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          <span>New Application</span>
        </Button>
      </div>

      <div className="space-y-4">
        {placeholderJobs.map((job) => (
          <Card key={job.id} className="hover:border-primary/50 transition-colors">
            <CardHeader className="p-4 pb-2">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-primary" />
                    <CardTitle className="text-base">{job.company}</CardTitle>
                  </div>
                  <CardDescription className="font-medium text-foreground">
                    {job.role}
                  </CardDescription>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                  {job.status}
                </span>
              </div>
            </CardHeader>
            <CardContent className="p-4 pt-2 flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {job.location}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  Deadline: {job.deadline}
                </span>
              </div>
              <Button variant="outline" size="sm">
                View Details
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
export default Applications
