import { NextResponse } from 'next/server';

export async function GET(request: Request, context: { params: { merchantId: string } }) {
  // Extract merchantId from context.params (await required in Next.js 15+)
  const { merchantId } = await context.params;

  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/recommendations/campaigns/${merchantId}`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer 1',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error fetching campaign recommendations: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in recommendations/campaigns API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch campaign recommendations' },
      { status: 500 }
    );
  }
}