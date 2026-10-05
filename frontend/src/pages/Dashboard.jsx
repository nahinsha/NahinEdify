import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  BookOpen,
  ClipboardList,
  FileText,
  GraduationCap,
  Send,
  Trophy,
  Users,
} from "lucide-react";
import { useAuth } from "../auth.js";
import {
  assignmentsApi,
  coursesApi,
  enrollmentsApi,
  lessonsApi,
  resultsApi,
  studentsApi,
  submissionsApi,
  teachersApi,
  getEnrollmentStats,
  getNotices,
} from "../api.js";
import {
  LineChart, //LineChart holo main container—mane graph-er pura area.
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
//Backend theke data ana already amra kore felechi...Recharts-er kaj shudhu:....“Je data React-er kache already ache, seta visual graph-e dekhano.”
import { Alert, PageHeader } from "../components/index.js";

// One tile per resource. `api` is the module from api.js the count comes from.
const tiles = [
  {
    address: "/teachers",
    text: "Teachers",
    api: teachersApi,
    icon: <Users size={16} className="text-indigo-500" />,
  },
  {
    address: "/students",
    text: "Students",
    api: studentsApi,
    icon: <GraduationCap size={16} className="text-indigo-500" />,
  },
  {
    address: "/courses",
    text: "Courses",
    api: coursesApi,
    icon: <BookOpen size={16} className="text-indigo-500" />,
  },
  {
    address: "/enrollments",
    text: "Enrollments",
    api: enrollmentsApi,
    icon: <ClipboardList size={16} className="text-indigo-500" />,
  },
  {
    address: "/lessons",
    text: "Lessons",
    api: lessonsApi,
    icon: <FileText size={16} className="text-indigo-500" />,
  },
  {
    address: "/assignments",
    text: "Assignments",
    api: assignmentsApi,
    icon: <ClipboardList size={16} className="text-indigo-500" />,
  },
  {
    address: "/submissions",
    text: "Submissions",
    api: submissionsApi,
    icon: <Send size={16} className="text-indigo-500" />,
  },
  {
    address: "/results",
    text: "Results",
    api: resultsApi,
    icon: <Trophy size={16} className="text-indigo-500" />,
  },
];

export default function Dashboard() {
  const { user } = useAuth();
  const [counts, setCounts] = useState({}); //dashboard-er tile-er count rakhar box
  const [enrollmentStats, setEnrollmentStats] = useState([]); //Enrollment graph-er data rakhar jonno ekta empty list-er state banalam।
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [notices, setNotices] = useState([]);

  // There is still no counts endpoint, but a paginated list reports how many
  // rows matched, so count() asks for one row and reads `count` off the
  // envelope. Eight tiles used to mean downloading eight whole tables.
  useEffect(() => {
    async function load() {
      try {
        const totals = await Promise.all(tiles.map((tile) => tile.api.count()));
        const stats = await getEnrollmentStats();
        console.log(stats);
        console.log(stats.map(item => item.total));
        setEnrollmentStats(stats); //Kintu stats ekhon sudhu load() function-er vitore ekta temporary variable. React UI eta theke directly graph banate parbe na, karon amader age data-ta state-e rakhte hobe।
        // console.log(stats);

        const noticeData = await getNotices();
        setNotices(noticeData.results);
        // console.log(noticeData.results);

        const nextCounts = {};
        tiles.forEach((tile, index) => {
          nextCounts[tile.text] = totals[index];
        });

        setCounts(nextCounts);
        setError("");
      } catch (problem) {
        setError(problem.message);
      } finally {
        setIsLoading(false);
      }
    }

    load();
  }, []);
  // useState lagbe API call korar jonno na; API call-er data-ta React component-er state hisebe rekhe UI-te use/update korar jonno useState lagche।

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.username ?? "there"}`}
        subtitle="Here’s a quick look at what’s happening today."
      />

      <Alert className="ml-auto w-fit max-w-md" onDismiss={() => setError("")}>
        {error}
      </Alert>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {tiles.map((tile) => (
          <Link
            key={tile.address}
            to={tile.address}
            className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:border-indigo-300"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-500">
                {tile.text}
              </span>
              {tile.icon}
            </div>
            <p className="mt-2 text-3xl font-semibold text-slate-900">
              {isLoading ? "—" : (counts[tile.text] ?? 0)}
            </p>
          </Link>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-[3fr_2fr] gap-6">
        {/* Graph */}
        <div>
          <h2 className="mb-3 text-lg font-semibold text-indigo-900">
            Student Enrollment Overview
          </h2>

          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={enrollmentStats}>
              <XAxis
                dataKey="enrollment_date"
                tickFormatter={(date) =>
                  new Date(date).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <CartesianGrid />
              <YAxis />
              <Line dataKey="total" stroke="#6f71c9" strokeWidth={1.5} />
              <Tooltip />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Notice Board */}
        <div>
          <h2 className="mb-3 text-lg font-semibold text-indigo-900">
            Notice Board
          </h2>

          <div className="rounded-xl border bg-white p-5 shadow-sm">
           
              {notices.map((notice) => (
                <div key={notice.id}>
                  <h1 className="text-base font-semibold text-slate-800"> 📢 {notice.title}</h1>
                  <p>{notice.message}</p>
                </div>
              ))}
           
          </div>
        </div>
      </div>
    </div>
  );
}
//X-axis-er value hisebe prottek object-er enrollment_date field-ta use koro
//Tooltip--> User jokhon graph-er kono data point-er upor mouse nibe, tokhon oi point-er information popup kore dekhao.
