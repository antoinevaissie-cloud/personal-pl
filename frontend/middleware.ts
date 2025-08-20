import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Routes that don't require authentication
const publicRoutes = ['/', '/login', '/register', '/api/health', '/test-auth']

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname
  
  // Check if it's a public route
  const isPublicRoute = publicRoutes.some(route => path === route || path.startsWith(`${route}/`))
  
  // Get token from cookies (we'll set this when user logs in)
  const token = request.cookies.get('pl_auth_token')
  
  // Redirect to login if accessing protected route without token
  if (!isPublicRoute && !token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', path)
    return NextResponse.redirect(loginUrl)
  }
  
  // Redirect to dashboard if accessing login/register with token
  if ((path === '/login' || path === '/register') && token) {
    return NextResponse.redirect(new URL('/pl', request.url))
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public).*)',
  ],
}