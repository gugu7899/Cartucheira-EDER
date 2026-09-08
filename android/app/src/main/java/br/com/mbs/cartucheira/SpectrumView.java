package br.com.mbs.cartucheira;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.View;

public class SpectrumView extends View {
    private final float[] levels = new float[24];
    private final float[] peaks = new float[24];
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    public SpectrumView(Context context) { super(context); }
    public void update(byte[] fft) {
        if (fft == null || fft.length < 8) return;
        int bins = fft.length / 2;
        for (int i=0;i<levels.length;i++) {
            int start = 1 + (int)(Math.pow((double)i/levels.length, 1.7)*(bins-2));
            int end = Math.max(start+1, 1 + (int)(Math.pow((double)(i+1)/levels.length,1.7)*(bins-2)));
            double sum=0; int count=0;
            for (int b=start;b<end && b<bins;b++) { int re=fft[2*b], im=fft[2*b+1]; sum += Math.sqrt(re*re+im*im); count++; }
            float target=(float)Math.min(1, Math.log1p(sum/Math.max(1,count))/5.0);
            levels[i] += (target-levels[i])*(target>levels[i] ? .55f : .20f);
            peaks[i] = Math.max(levels[i],peaks[i]-.035f);
        }
        invalidate();
    }
    public void clear() { for(int i=0;i<24;i++){levels[i]=0;peaks[i]=0;} invalidate(); }
    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas); float gap=3*getResources().getDisplayMetrics().density; float w=(getWidth()-gap*23)/24f; float h=getHeight()-4;
        for(int i=0;i<24;i++) { float x=i*(w+gap); float bh=Math.max(2,h*levels[i]); paint.setColor(Color.rgb(255,122+(int)(50*levels[i]),0)); canvas.drawRoundRect(x,getHeight()-bh,x+w,getHeight(),3,3,paint); if(peaks[i]>.08){paint.setColor(0xffffedcc);float y=Math.max(0,getHeight()-h*peaks[i]-2);canvas.drawRect(x,y,x+w,y+2,paint);} }
    }
}
