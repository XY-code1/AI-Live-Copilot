import { NextResponse, type NextFetchEvent, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/register"];

export default function proxy(request: NextRequest, event: NextFetchEvent) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("ailc_token")?.value;

  if (!token && !PUBLIC_PATHS.some((path) => pathname.startsWith(path))) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return NextResponse.redirect(url);
  }
  if (token && PUBLIC_PATHS.some((path) => pathname.startsWith(path))) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next|.*\\..*).*)", "/(api|trpc)(.*)"],
};
