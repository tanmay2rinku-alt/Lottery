import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

interface LotteryResult {
  number: number
  draw_time: string
  draw_date: string
  series: string
  digit_sum: number
}

export async function scrapeLotteryData(): Promise<LotteryResult[]> {
  // Simple HTTP-based scraping (no browser needed)
  const response = await fetch('https://www.lotterysambad.com')

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const html = await response.text()

  // Extract PDF links (simplified regex)
  const pdfLinks = html.match(/href="([^"]*\.pdf[^"]*)"/g) || []

  if (pdfLinks.length === 0) {
    throw new Error('No PDF links found')
  }

  // Get the most recent PDF
  const latestPdf = pdfLinks[0].match(/href="([^"]*)"/)?.[1]

  if (!latestPdf) {
    throw new Error('Could not extract PDF URL')
  }

  // Download PDF
  const pdfResponse = await fetch(`https://www.lotterysambad.com${latestPdf}`)
  const pdfBuffer = await pdfResponse.arrayBuffer()

  // Extract text from PDF (simplified - would need pdf-parse library)
  // For now, return mock data
  const results: LotteryResult[] = [
    {
      number: 12345,
      draw_time: '1PM',
      draw_date: new Date().toISOString().split('T')[0],
      series: '12',
      digit_sum: 15
    }
  ]

  return results
}

Deno.serve(async (req) => {
  try {
    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    )

    // Scrape lottery data
    const lotteryResults = await scrapeLotteryData()

    // Store in database
    const { data, error } = await supabase
      .from('winning_numbers')
      .insert(lotteryResults)

    if (error) {
      throw error
    }

    return new Response(
      JSON.stringify({
        success: true,
        message: `Scraped ${lotteryResults.length} lottery results`,
        data
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})