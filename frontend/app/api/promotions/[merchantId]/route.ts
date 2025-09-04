import { NextResponse } from 'next/server';

export async function GET(request: Request, context: { params: { merchantId: string } }) {
  // Extract merchantId from context.params (await required in Next.js 15+)
  const { merchantId } = await context.params;
  
  try {
    // Use hardcoded token '1' since environment variables aren't available server-side
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/promotions/${merchantId}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Error fetching promotions: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in promotions API route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch promotions' },
      { status: 500 }
    );
  }
}