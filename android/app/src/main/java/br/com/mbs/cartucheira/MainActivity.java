package br.com.mbs.cartucheira;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.media.audiofx.Visualizer;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.GridLayout;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

public class MainActivity extends Activity {
    private static final String[] DEFAULT_NAMES={"Bip de chamada","Vinheta curta","Abertura de transmissão","Encerramento","Alerta curto","Sinal de atenção","Transição de bloco","Chamada de operador","Ruído de sintonia","Identificação de estação","Efeito de passagem","Sinal eletrônico","Aviso curto","Campainha rádio","Pulso de comunicação","Confirmação","Entrada de boletim","Saída de boletim","Efeito digital","Efeito analógico","Rádio antigo","Interferência curta","Frequência abrindo","Frequência fechando","Alerta técnico","Chamada urgente","Sinal de conexão","Efeito de transmissão","Efeito de encerramento","Transição musical","Impacto sonoro","Sinal especial","Efeito ambiente","Chamada extra","Reserva","Reserva"};
    private static final int PICK_AUDIO=200, PICK_SYMBOL=201, EXPORT_BACKUP=202, IMPORT_BACKUP=203;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final List<Integer> queue=new ArrayList<>();
    private final CartView[] carts=new CartView[36];
    private SharedPreferences prefs; private LinearLayout root; private GridLayout grid; private MediaPlayer player; private Visualizer visualizer;
    private Button lockButton,queueButton; private ImageView symbol; private TextView identity; private int current=-1,pendingCart=-1; private long startedAt; private boolean locked=false,queueMode=false;
    private int bg,panel,cartA,cartB,fg,accent;

    @Override public void onCreate(Bundle state){super.onCreate(state);setVolumeControlStream(AudioManager.STREAM_MUSIC);prefs=getSharedPreferences("cartucheira",MODE_PRIVATE);applyThemeValues(prefs.getString("theme","Escuro Padrão"));build();requestAudioPermission();handler.post(ticker);}
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private GradientDrawable shape(int color,int stroke,int strokeColor,int radius){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));if(stroke>0)d.setStroke(dp(stroke),strokeColor);return d;}
    private TextView text(String value,int size){TextView t=new TextView(this);t.setText(value);t.setTextColor(fg);t.setTextSize(size);t.setGravity(Gravity.CENTER_VERTICAL);return t;}
    private Button action(String value){Button b=new Button(this);b.setText(value);b.setTextColor(fg);b.setTextSize(11);b.setAllCaps(false);b.setBackground(shape(panel,1,0xff4a4d51,7));return b;}

    private void build(){
        root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setPadding(dp(9),dp(7),dp(9),dp(5));root.setBackgroundColor(bg);setContentView(root);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);top.setPadding(0,0,0,dp(6));root.addView(top,new LinearLayout.LayoutParams(-1,dp(94)));
        LinearLayout volumeBox=new LinearLayout(this);volumeBox.setOrientation(LinearLayout.VERTICAL);TextView vh=text("VOLUME GERAL",12);vh.setGravity(Gravity.CENTER);vh.setTypeface(null,1);volumeBox.addView(vh,new LinearLayout.LayoutParams(-1,dp(25)));LinearLayout volumeLine=new LinearLayout(this);volumeLine.setGravity(Gravity.CENTER_VERTICAL);volumeLine.addView(text("🔊",18),new LinearLayout.LayoutParams(dp(34),-1));SeekBar volume=new SeekBar(this);volume.setMax(100);volume.setProgress(prefs.getInt("volume",80));volumeLine.addView(volume,new LinearLayout.LayoutParams(dp(165),-1));TextView volumeText=text(volume.getProgress()+"%",11);volumeLine.addView(volumeText,new LinearLayout.LayoutParams(dp(48),-1));volume.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){public void onProgressChanged(SeekBar b,int v,boolean user){volumeText.setText(v+"%");prefs.edit().putInt("volume",v).apply();if(player!=null)player.setVolume(v/100f,v/100f);}public void onStartTrackingTouch(SeekBar b){}public void onStopTrackingTouch(SeekBar b){}});volumeBox.addView(volumeLine,new LinearLayout.LayoutParams(-1,dp(55)));top.addView(volumeBox,new LinearLayout.LayoutParams(0,-1,1));
        LinearLayout brand=new LinearLayout(this);brand.setOrientation(LinearLayout.VERTICAL);brand.setGravity(Gravity.CENTER);symbol=new ImageView(this);symbol.setScaleType(ImageView.ScaleType.CENTER_INSIDE);brand.addView(symbol,new LinearLayout.LayoutParams(dp(100),dp(62)));identity=text(prefs.getString("app_name","MBS"),19);identity.setTypeface(null,1);identity.setGravity(Gravity.CENTER);brand.addView(identity,new LinearLayout.LayoutParams(dp(190),dp(28)));top.addView(brand,new LinearLayout.LayoutParams(dp(210),-1));loadSymbol();
        LinearLayout transmission=new LinearLayout(this);transmission.setOrientation(LinearLayout.VERTICAL);transmission.setPadding(dp(4),0,dp(4),0);lockButton=action("🔒 BLOQUEAR");lockButton.setOnClickListener(v->toggleLock());transmission.addView(lockButton,new LinearLayout.LayoutParams(dp(145),0,1));queueButton=action("☷ EM FILA");queueButton.setOnClickListener(v->toggleQueue());LinearLayout.LayoutParams qp=new LinearLayout.LayoutParams(dp(145),0,1);qp.topMargin=dp(4);transmission.addView(queueButton,qp);top.addView(transmission,new LinearLayout.LayoutParams(dp(153),-1));
        Button settings=action("⚙");settings.setTextSize(21);settings.setOnClickListener(this::settingsMenu);top.addView(settings,new LinearLayout.LayoutParams(dp(55),dp(58)));
        ScrollView scroll=new ScrollView(this);grid=new GridLayout(this);grid.setPadding(0,0,0,dp(5));scroll.addView(grid,new ScrollView.LayoutParams(-1,-2));root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        int columns=getResources().getConfiguration().smallestScreenWidthDp>=720?6:(getResources().getConfiguration().screenWidthDp>=600?4:2);grid.setColumnCount(columns);
        for(int i=0;i<36;i++){carts[i]=new CartView(i);GridLayout.LayoutParams p=new GridLayout.LayoutParams();p.width=0;p.height=dp(columns>=6?126:142);p.columnSpec=GridLayout.spec(GridLayout.UNDEFINED,1f);p.setMargins(dp(3),dp(3),dp(3),dp(3));grid.addView(carts[i],p);}
        LinearLayout footer=new LinearLayout(this);TextView fixed=text("Cartucheira MBS",12);TextView developer=text("Desenvolvedor Marcelo Soares",12);developer.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);footer.addView(fixed,new LinearLayout.LayoutParams(0,dp(28),1));footer.addView(developer,new LinearLayout.LayoutParams(0,dp(28),1));root.addView(footer);
    }

    private class CartView extends FrameLayout {
        final int index; final TextView number,name,time,badge; final ImageButton menu; final SpectrumView spectrum; final ProgressBar progress;
        CartView(int i){super(MainActivity.this);index=i;setPadding(dp(7),dp(5),dp(7),dp(5));setBackground(cardBackground(i,false,false));setOnClickListener(v->trigger(i));
            LinearLayout box=new LinearLayout(MainActivity.this);box.setOrientation(LinearLayout.VERTICAL);addView(box,new FrameLayout.LayoutParams(-1,-1));LinearLayout head=new LinearLayout(MainActivity.this);head.setGravity(Gravity.CENTER_VERTICAL);number=text(String.format("%02d",i+1),12);number.setTypeface(null,1);head.addView(number,new LinearLayout.LayoutParams(dp(35),dp(27)));badge=text("",9);badge.setTextColor(accent);badge.setTypeface(null,1);head.addView(badge,new LinearLayout.LayoutParams(0,dp(27),1));menu=new ImageButton(MainActivity.this);menu.setImageResource(android.R.drawable.ic_menu_more);menu.setColorFilter(fg);menu.setBackgroundColor(Color.TRANSPARENT);menu.setOnClickListener(v->{showCartMenu(i,v);});head.addView(menu,new LinearLayout.LayoutParams(dp(34),dp(30)));box.addView(head);
            name=text(prefs.getString("name_"+i,DEFAULT_NAMES[i]),15);name.setGravity(Gravity.CENTER);name.setTypeface(null,1);box.addView(name,new LinearLayout.LayoutParams(-1,0,1));time=text("",10);time.setGravity(Gravity.CENTER);box.addView(time,new LinearLayout.LayoutParams(-1,dp(18)));spectrum=new SpectrumView(MainActivity.this);spectrum.setVisibility(GONE);box.addView(spectrum,new LinearLayout.LayoutParams(-1,dp(24)));progress=new ProgressBar(MainActivity.this,null,android.R.attr.progressBarStyleHorizontal);progress.setMax(1000);progress.setProgressTintList(android.content.res.ColorStateList.valueOf(0xffff8a00));box.addView(progress,new LinearLayout.LayoutParams(-1,dp(4)));}
        void state(boolean playing){spectrum.setVisibility(playing?VISIBLE:GONE);time.setVisibility(playing?VISIBLE:INVISIBLE);if(!playing){time.setText("");progress.setProgress(0);spectrum.clear();}setBackground(cardBackground(index,playing,queue.contains(index)));}
        void queued(int position){badge.setText(position>0?"FILA "+position:"");setBackground(cardBackground(index,index==current,position>0));}
    }
    private GradientDrawable cardBackground(int i,boolean playing,boolean queued){int custom=prefs.getInt("color_"+i,0);int color=custom!=0?custom:(((i/6+i%6)%2==0)?cartA:cartB);return shape(color,playing?2:1,playing||queued?accent:0xff55585d,8);}

    private void trigger(int index){
        if(queueMode&&current>=0&&player!=null&&player.isPlaying()){if(index==current)return;if(queue.contains(index))queue.remove((Integer)index);else queue.add(index);refreshQueue();return;}
        if(index==current&&player!=null){fadeOut(true);return;}play(index);
    }
    private void play(int index){stopPlayer(false);try{player=new MediaPlayer();String file=prefs.getString("audio_"+index,"");if(file.isEmpty()){android.content.res.AssetFileDescriptor afd=getAssets().openFd("audio/"+String.format("%02d.wav",index+1));player.setDataSource(afd.getFileDescriptor(),afd.getStartOffset(),afd.getLength());afd.close();}else player.setDataSource(file);player.prepare();float v=prefs.getInt("volume",80)/100f;player.setVolume(v,v);player.setOnCompletionListener(m->{stopPlayer(false);playNext();});current=index;startedAt=System.currentTimeMillis();carts[index].state(true);player.start();startVisualizer();}catch(Exception e){stopPlayer(false);Toast.makeText(this,"Não foi possível reproduzir este áudio.",Toast.LENGTH_LONG).show();}}
    private void stopPlayer(boolean clearQueue){if(visualizer!=null){visualizer.release();visualizer=null;}if(player!=null){try{player.stop();}catch(Exception ignored){}player.release();player=null;}if(current>=0)carts[current].state(false);current=-1;if(clearQueue){queue.clear();refreshQueue();}}
    private void fadeOut(boolean advance){if(player==null)return;final int steps=13;for(int s=1;s<=steps;s++){final int step=s;handler.postDelayed(()->{if(player==null)return;float base=prefs.getInt("volume",80)/100f;float v=base*(1-step/(float)steps);player.setVolume(v,v);if(step==steps){stopPlayer(false);if(advance)playNext();}},s*50L);}}
    private void playNext(){if(!queue.isEmpty()){int next=queue.remove(0);refreshQueue();play(next);}}
    private void toggleQueue(){queueMode=!queueMode;if(!queueMode)queue.clear();queueButton.setText(queueMode?(queue.isEmpty()?"☷ EM FILA":"☷ EM FILA ("+queue.size()+")"):"☷ EM FILA");queueButton.setBackground(shape(queueMode?accent:panel,1,queueMode?accent:0xff4a4d51,7));refreshQueue();}
    private void refreshQueue(){for(CartView c:carts)if(c!=null)c.queued(0);for(int i=0;i<queue.size();i++)carts[queue.get(i)].queued(i+1);queueButton.setText(queueMode&& !queue.isEmpty()?"☷ EM FILA ("+queue.size()+")":"☷ EM FILA");}
    private void toggleLock(){locked=!locked;lockButton.setText(locked?"🔓 DESBLOQUEAR":"🔒 BLOQUEAR");lockButton.setBackground(shape(locked?accent:panel,1,locked?accent:0xff4a4d51,7));for(CartView c:carts)c.menu.setVisibility(locked?View.GONE:View.VISIBLE);}
    private final Runnable ticker=new Runnable(){public void run(){if(player!=null&&current>=0){int elapsed=(int)((System.currentTimeMillis()-startedAt)/1000),duration=Math.max(1,player.getDuration()/1000);carts[current].time.setText(stamp(elapsed)+" / "+stamp(duration));carts[current].progress.setProgress(Math.min(1000,elapsed*1000/duration));}handler.postDelayed(this,100);}};
    private String stamp(int s){return String.format("%02d:%02d",s/60,s%60);}
    private void startVisualizer(){try{visualizer=new Visualizer(player.getAudioSessionId());visualizer.setCaptureSize(Visualizer.getCaptureSizeRange()[1]);visualizer.setDataCaptureListener(new Visualizer.OnDataCaptureListener(){public void onWaveFormDataCapture(Visualizer v,byte[] w,int rate){}public void onFftDataCapture(Visualizer v,byte[] fft,int rate){runOnUiThread(()->{if(current>=0)carts[current].spectrum.update(fft);});}},Visualizer.getMaxCaptureRate()/2,false,true);visualizer.setEnabled(true);}catch(Exception ignored){visualizer=null;}}
    private void requestAudioPermission(){if(android.os.Build.VERSION.SDK_INT>=23&&checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},44);}

    private void showCartMenu(int i,View anchor){PopupMenu m=new PopupMenu(this,anchor);m.getMenu().add("Trocar áudio…");m.getMenu().add("Renomear…");m.getMenu().add("Cor laranja");m.getMenu().add("Cor azul");m.getMenu().add("Cor verde");m.getMenu().add("Restaurar cor");m.getMenu().add("Limpar");m.setOnMenuItemClickListener(item->{String t=item.getTitle().toString();if(t.startsWith("Trocar")){pendingCart=i;Intent x=new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("audio/*").addCategory(Intent.CATEGORY_OPENABLE);startActivityForResult(x,PICK_AUDIO);}else if(t.startsWith("Renomear"))rename(i);else if(t.equals("Cor laranja"))setCartColor(i,0xff7a3c08);else if(t.equals("Cor azul"))setCartColor(i,0xff123d68);else if(t.equals("Cor verde"))setCartColor(i,0xff145236);else if(t.equals("Restaurar cor"))setCartColor(i,0);else if(t.equals("Limpar")){prefs.edit().putString("name_"+i,"").putString("audio_"+i,"").apply();carts[i].name.setText("");}return true;});m.show();}
    private void rename(int i){final android.widget.EditText input=new android.widget.EditText(this);input.setText(carts[i].name.getText());new AlertDialog.Builder(this).setTitle("Renomear cartucho").setView(input).setPositiveButton("SALVAR",(d,w)->{String n=input.getText().toString().trim();prefs.edit().putString("name_"+i,n).apply();carts[i].name.setText(n);}).setNegativeButton("CANCELAR",null).show();}
    private void setCartColor(int i,int color){prefs.edit().putInt("color_"+i,color).apply();carts[i].state(i==current);}

    private void settingsMenu(View anchor){if(locked)return;PopupMenu m=new PopupMenu(this,anchor);m.getMenu().add("Importar programação…");m.getMenu().add("Exportar programação…");m.getMenu().add("Alterar tema…");m.getMenu().add("Alterar nome…");m.getMenu().add("Trocar símbolo…");m.getMenu().add("Restaurar configurações");m.setOnMenuItemClickListener(item->{String t=item.getTitle().toString();if(t.startsWith("Importar"))startActivityForResult(new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("application/zip").addCategory(Intent.CATEGORY_OPENABLE),IMPORT_BACKUP);else if(t.startsWith("Exportar"))startActivityForResult(new Intent(Intent.ACTION_CREATE_DOCUMENT).setType("application/zip").putExtra(Intent.EXTRA_TITLE,"Cartucheira-MBS-backup.mbs"),EXPORT_BACKUP);else if(t.startsWith("Alterar tema"))chooseTheme();else if(t.startsWith("Alterar nome"))renameApp();else if(t.startsWith("Trocar símbolo"))startActivityForResult(new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("image/*").addCategory(Intent.CATEGORY_OPENABLE),PICK_SYMBOL);else restore();return true;});m.show();}
    private void chooseTheme(){String[] names={"Escuro Padrão","Preto Estúdio","Cinza Console","Azul Estúdio","Verde Estúdio"};new AlertDialog.Builder(this).setTitle("Escolha o tema").setItems(names,(d,which)->{prefs.edit().putString("theme",names[which]).apply();recreate();}).show();}
    private void renameApp(){final android.widget.EditText input=new android.widget.EditText(this);input.setText(identity.getText());new AlertDialog.Builder(this).setTitle("Nome da cartucheira").setView(input).setPositiveButton("SALVAR",(d,w)->{String n=input.getText().toString().trim();if(!n.isEmpty()){prefs.edit().putString("app_name",n).apply();identity.setText(n);}}).setNegativeButton("CANCELAR",null).show();}
    private void restore(){new AlertDialog.Builder(this).setTitle("Restaurar configurações?").setMessage("Os nomes, cores, áudios e tema voltarão ao padrão.").setPositiveButton("RESTAURAR",(d,w)->{stopPlayer(true);prefs.edit().clear().apply();recreate();}).setNegativeButton("CANCELAR",null).show();}
    private void applyThemeValues(String name){int[] c;if(name.equals("Azul Estúdio"))c=new int[]{0xff071525,0xff0b2139,0xff102b49,0xff153657,0xffedf6ff,0xff268cff};else if(name.equals("Verde Estúdio"))c=new int[]{0xff06130e,0xff0a2017,0xff0e2a1e,0xff133526,0xffeffff6,0xff20c878};else if(name.equals("Cinza Console"))c=new int[]{0xff202226,0xff292c31,0xff303338,0xff383b40,0xfff5f5f5,0xffff9b22};else if(name.equals("Preto Estúdio"))c=new int[]{0xff050505,0xff0a0a0a,0xff101010,0xff171717,0xffffffff,0xffff7900};else c=new int[]{0xff0d0e10,0xff15171a,0xff17191b,0xff1d2024,0xfff3f3f3,0xffff8a00};bg=c[0];panel=c[1];cartA=c[2];cartB=c[3];fg=c[4];accent=c[5];}
    private void loadSymbol(){String path=prefs.getString("symbol","");if(!path.isEmpty()&&new File(path).exists())symbol.setImageBitmap(BitmapFactory.decodeFile(path));else try{symbol.setImageBitmap(BitmapFactory.decodeStream(getAssets().open("logo.png")));}catch(Exception ignored){}}

    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(result!=RESULT_OK||data==null||data.getData()==null)return;Uri uri=data.getData();try{if(request==PICK_AUDIO&&pendingCart>=0){File dir=new File(getFilesDir(),"audio");dir.mkdirs();File dst=new File(dir,"cart_"+pendingCart+".audio");copy(getContentResolver().openInputStream(uri),new FileOutputStream(dst));prefs.edit().putString("audio_"+pendingCart,dst.getAbsolutePath()).apply();}else if(request==PICK_SYMBOL){File dst=new File(getFilesDir(),"symbol.img");copy(getContentResolver().openInputStream(uri),new FileOutputStream(dst));prefs.edit().putString("symbol",dst.getAbsolutePath()).apply();loadSymbol();}else if(request==EXPORT_BACKUP)exportBackup(uri);else if(request==IMPORT_BACKUP)importBackup(uri);}catch(Exception e){Toast.makeText(this,"Não foi possível concluir a operação.",Toast.LENGTH_LONG).show();}pendingCart=-1;}
    private void copy(InputStream in,OutputStream out)throws Exception{byte[] b=new byte[16384];int n;while((n=in.read(b))>0)out.write(b,0,n);in.close();out.close();}
    private JSONObject configJson()throws Exception{JSONObject o=new JSONObject();o.put("app_name",prefs.getString("app_name","MBS"));o.put("theme",prefs.getString("theme","Escuro Padrão"));o.put("volume",prefs.getInt("volume",80));JSONArray a=new JSONArray();for(int i=0;i<36;i++){JSONObject c=new JSONObject();c.put("name",prefs.getString("name_"+i,DEFAULT_NAMES[i]));c.put("color",prefs.getInt("color_"+i,0));c.put("custom",!prefs.getString("audio_"+i,"").isEmpty());a.put(c);}o.put("carts",a);return o;}
    private void exportBackup(Uri uri)throws Exception{ZipOutputStream z=new ZipOutputStream(getContentResolver().openOutputStream(uri));z.putNextEntry(new ZipEntry("config.json"));z.write(configJson().toString(2).getBytes("UTF-8"));z.closeEntry();for(int i=0;i<36;i++){String p=prefs.getString("audio_"+i,"");if(!p.isEmpty()&&new File(p).exists()){z.putNextEntry(new ZipEntry("audio/cart_"+i+".audio"));FileInputStream in=new FileInputStream(p);byte[] b=new byte[16384];int n;while((n=in.read(b))>0)z.write(b,0,n);in.close();z.closeEntry();}}String s=prefs.getString("symbol","");if(!s.isEmpty()&&new File(s).exists()){z.putNextEntry(new ZipEntry("symbol.img"));FileInputStream in=new FileInputStream(s);byte[] b=new byte[16384];int n;while((n=in.read(b))>0)z.write(b,0,n);in.close();z.closeEntry();}z.close();Toast.makeText(this,"Programação exportada.",Toast.LENGTH_SHORT).show();}
    private void importBackup(Uri uri)throws Exception{File temp=new File(getCacheDir(),"import.mbs");copy(getContentResolver().openInputStream(uri),new FileOutputStream(temp));ZipInputStream z=new ZipInputStream(new FileInputStream(temp));ZipEntry e;JSONObject config=null;File dir=new File(getFilesDir(),"audio");dir.mkdirs();while((e=z.getNextEntry())!=null){if(e.getName().equals("config.json")){java.io.ByteArrayOutputStream out=new java.io.ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=z.read(b))>0)out.write(b,0,n);config=new JSONObject(out.toString("UTF-8"));}else if(e.getName().startsWith("audio/cart_")){File dst=new File(dir,new File(e.getName()).getName());FileOutputStream out=new FileOutputStream(dst);byte[] b=new byte[8192];int n;while((n=z.read(b))>0)out.write(b,0,n);out.close();}else if(e.getName().equals("symbol.img")){FileOutputStream out=new FileOutputStream(new File(getFilesDir(),"symbol.img"));byte[] b=new byte[8192];int n;while((n=z.read(b))>0)out.write(b,0,n);out.close();}z.closeEntry();}z.close();if(config==null)throw new Exception("Backup inválido");SharedPreferences.Editor ed=prefs.edit().clear().putString("app_name",config.optString("app_name","MBS")).putString("theme",config.optString("theme","Escuro Padrão")).putInt("volume",config.optInt("volume",80));JSONArray a=config.getJSONArray("carts");for(int i=0;i<36;i++){JSONObject c=a.getJSONObject(i);ed.putString("name_"+i,c.optString("name",DEFAULT_NAMES[i])).putInt("color_"+i,c.optInt("color",0));File f=new File(dir,"cart_"+i+".audio");if(c.optBoolean("custom")&&f.exists())ed.putString("audio_"+i,f.getAbsolutePath());}File s=new File(getFilesDir(),"symbol.img");if(s.exists())ed.putString("symbol",s.getAbsolutePath());ed.apply();recreate();}
    @Override protected void onDestroy(){handler.removeCallbacksAndMessages(null);stopPlayer(false);super.onDestroy();}
}
